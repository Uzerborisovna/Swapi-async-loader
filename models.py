from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class SwapiPeople(Base):
    __tablename__ = "people"

    id: Mapped[str] = mapped_column(primary_key=True)
    birth_year: Mapped[str] = mapped_column(default="")
    eye_color: Mapped[str] = mapped_column(default="")
    films: Mapped[str] = mapped_column(default="")
    gender: Mapped[str] = mapped_column(default="")
    hair_color: Mapped[str] = mapped_column(default="")
    height: Mapped[str] = mapped_column(default="")
    homeworld: Mapped[str] = mapped_column(default="")
    mass: Mapped[str] = mapped_column(default="")
    name: Mapped[str] = mapped_column(default="")
    skin_color: Mapped[str] = mapped_column(default="")
    starships: Mapped[str] = mapped_column(default="")
    vehicles: Mapped[str] = mapped_column(default="")