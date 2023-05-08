import os

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from sqlalchemy import String, ForeignKey, create_engine, select, delete
from typing import *
from sqlite3 import Time
from datetime import timedelta


class Base(DeclarativeBase):
    pass


class Save(Base):
    __tablename__ = "save"
    id: Mapped[int] = mapped_column(primary_key=True)
    level_progress: Mapped[int | None]
    language: Mapped[str]
    keyboard_layout: Mapped[str]


class Level(Base):
    __tablename__ = "level"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str | None]


class GamePrinciple(Base):
    __tablename__ = "game_principle"
    id: Mapped[int] = mapped_column(primary_key=True)


class Run(Base):
    __tablename__ = "run"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    save_id: Mapped[int] = mapped_column(ForeignKey("save.id"))
    save: Mapped[Save] = relationship()
    level_id: Mapped[int] = mapped_column(ForeignKey("level.id"))
    level: Mapped[Level] = relationship()
    game_principle_id: Mapped[int] = mapped_column(ForeignKey("game_principle.id"))
    game_principle: Mapped[GamePrinciple] = relationship()

    preset_text: Mapped[Text]
    typed_text: Mapped[Text]
    time_taken_for_level: Mapped[Time]


# Speicherverbrauch evtl. Optimieren
class Char(Base):
    __tablename__ = "char"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("run.id"))
    run: Mapped[Run] = relationship(back_populates="chars")

    char: Mapped[str]
    preset_char_count: Mapped[int]
    typed_char_count: Mapped[int]
    avg_time_per_char: Mapped[timedelta]
    accuracy: Mapped[float]


os.makedirs("data", exist_ok=True)

engine = create_engine("sqlite:///data/database.sqlite", echo=True)
Base.metadata.create_all(engine)


def new_session():
    return Session(engine)


with Session(engine) as session:
    s = Save(
        language="German",
    )

    session.add(s)
    session.commit()

    result = session.execute(select(Save))
    print(select(Save).where(Save.level_progress == 1))
    print(result.all())

    session.execute(delete(Save))
    session.commit()

pass
