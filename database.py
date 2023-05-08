import os

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from sqlalchemy import String, ForeignKey, create_engine, select, delete
from typing import *
from datetime import timedelta



class Base(DeclarativeBase):
    pass


class Save(Base):
    __tablename__ = "save"
    id: Mapped[int] = mapped_column(primary_key=True)
    settings: Mapped[str]
    level_progress: Mapped[int | None]


class Level(Base):
    __tablename__ = "level"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str | None]


class GamePrinciple(Base):
    __tablename__ = "game_principle"
    id: Mapped[int] = mapped_column(primary_key=True)


class Run(Base):
    __tablename__ = "run"
    id: Mapped[int] = mapped_column(primary_key=True)
    save_id: Mapped[int] = mapped_column(ForeignKey("save.id"))
    save: Mapped[Save] = relationship()
    level_id: Mapped[int] = mapped_column(ForeignKey("level.id"))
    level: Mapped[Level] = relationship()
    game_principle_id: Mapped[int] = mapped_column(ForeignKey("game_principle.id"))
    game_principle: Mapped[GamePrinciple] = relationship()

    characters_used: Mapped[str]
    preset_text: Mapped[str]
    typed_text: Mapped[str]
    time_taken: Mapped[timedelta]
    accuracy: Mapped[float]
    real_avg_speed: Mapped[float]
    logical_avg_speed: Mapped[float]
    chars: Mapped[List["Char"]] = relationship(back_populates="run")


class Char(Base):
    __tablename__ = "char"
    run_id: Mapped[int] = mapped_column(ForeignKey("run.id"), primary_key=True)
    run: Mapped[Run] = relationship(back_populates="chars")
    char: Mapped[int] = mapped_column(primary_key=True)

    accuracy: Mapped[float]
    speed: Mapped[float]


os.makedirs("data", exist_ok=True)

engine = create_engine("sqlite:///data/database.sqlite", echo=True)
Base.metadata.create_all(engine)


def new_session():
    return Session(engine)


with Session(engine) as session:
    s = Save(
        settings="bruh",
    )

    session.add(s)
    session.commit()

    result = session.execute(select(Save))
    print(select(Save).where(Save.level_progress == 1))
    print(result.all())

    session.execute(delete(Save))
    session.commit()

pass






