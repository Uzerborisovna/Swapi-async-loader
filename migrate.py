import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from models import Base

# Настройки подключения к базе (из docker-compose.yml)
DB_URL = "postgresql+asyncpg://swapi_user:swapi_pass@localhost:5433/swapi"

async def main():
    engine = create_async_engine(DB_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Таблица успешно создана!")

if __name__ == "__main__":
    asyncio.run(main())