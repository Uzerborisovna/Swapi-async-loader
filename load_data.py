import asyncio
import aiohttp
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models import SwapiPeople

# Базовый URL API
BASE_URL = "https://swapi-node.vercel.app"
# URL для подключения к базе (порт 5433, как мы поменяли)
DB_URL = "postgresql+asyncpg://swapi_user:swapi_pass@localhost:5433/swapi"


async def fetch(session, url):
    """Асинхронный GET-запрос. Возвращает JSON."""
    async with session.get(url) as response:
        return await response.json()


async def get_related(session, urls, field):
    """По списку путей делает запросы и собирает нужное поле через запятую."""
    if not urls:
        return ""
    tasks = [fetch(session, BASE_URL + path) for path in urls]
    results = await asyncio.gather(*tasks)
    # API возвращает объект с ключом fields, внутри которого лежит нужное поле
    return ", ".join([item["fields"][field] for item in results])


async def get_homeworld(session, path):
    """Получает название родной планеты."""
    if not path:
        return ""
    data = await fetch(session, BASE_URL + path)
    return data["fields"]["name"]


async def process_character(session, character):
    """Обрабатывает одного персонажа: достаёт связанные данные и формирует запись."""
    fields = character["fields"]
    # ID берём из url: /api/people/1 -> "1"
    char_id = fields["url"].rstrip("/").split("/")[-1]

    # Параллельно запрашиваем homeworld, films, starships, vehicles
    homeworld_task = get_homeworld(session, fields.get("homeworld"))
    films_task = get_related(session, fields.get("films"), "title")
    starships_task = get_related(session, fields.get("starships"), "starship_class")
    vehicles_task = get_related(session, fields.get("vehicles"), "name")

    homeworld, films, starships, vehicles = await asyncio.gather(
        homeworld_task, films_task, starships_task, vehicles_task
    )

    return SwapiPeople(
        id=char_id,
        birth_year=fields.get("birth_year", ""),
        eye_color=fields.get("eye_color", ""),
        films=films,
        gender=fields.get("gender", ""),
        hair_color=fields.get("hair_color", ""),
        height=fields.get("height", ""),
        homeworld=homeworld,
        mass=fields.get("mass", ""),
        name=fields.get("name", ""),
        skin_color=fields.get("skin_color", ""),
        starships=starships,
        vehicles=vehicles,
    )


async def load_all():
    """Загружает всех персонажей через пагинацию."""
    async with aiohttp.ClientSession() as session:
        # Получаем первую страницу, чтобы узнать общее количество страниц
        first_page = await fetch(session, f"{BASE_URL}/api/people?page=1&limit=10")
        total_pages = first_page["pages"]

        # Собираем все страницы
        tasks = [
            fetch(session, f"{BASE_URL}/api/people?page={p}&limit=10")
            for p in range(1, total_pages + 1)
        ]
        pages = await asyncio.gather(*tasks)

        # Извлекаем всех персонажей
        characters = []
        for page in pages:
            characters.extend(page["results"])

        print(f"Получено персонажей: {len(characters)}")

        # Обрабатываем каждого персонажа параллельно
        tasks = [process_character(session, ch) for ch in characters]
        people = await asyncio.gather(*tasks)

        # Сохраняем в базу
        engine = create_async_engine(DB_URL, echo=False)
        async_session = async_sessionmaker(engine, expire_on_commit=False)

        async with async_session() as session_db:
            session_db.add_all(people)
            await session_db.commit()

        await engine.dispose()
        print(f"Сохранено в БД: {len(people)} персонажей")


if __name__ == "__main__":
    asyncio.run(load_all())