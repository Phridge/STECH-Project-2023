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
    settings: Mapped[bytes | None]

    runs: Mapped[List["Run"]] = relationship(back_populates="save", cascade="all,delete")


class Level(Base):
    __tablename__ = "level"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]


class GamePrinciple(Base):
    __tablename__ = "game_principle"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]


class Run(Base):
    __tablename__ = "run"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    save_id: Mapped[int] = mapped_column(ForeignKey("save.id", ondelete="CASCADE"))
    save: Mapped[Save] = relationship(back_populates="runs")

    level_id: Mapped[int] = mapped_column(ForeignKey("level.id"))
    level: Mapped[Level] = relationship()
    # game_principle_id: Mapped[int] = mapped_column(ForeignKey("game_principle.id"))
    # game_principle: Mapped[GamePrinciple] = relationship()

    preset_text: Mapped[Text]
    typed_text: Mapped[Text]
    char_count: Mapped[int]
    time: Mapped[float]
    correct_char_count: Mapped[int]
    correct_time: Mapped[float]
    chars: Mapped[List["Char"]] = relationship(back_populates="run", cascade="all,delete")


# Speicherverbrauch evtl. Optimieren
class Char(Base):
    __tablename__ = "char"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    run_id: Mapped[int] = mapped_column(ForeignKey("run.id", ondelete="CASCADE"))
    run: Mapped[Run] = relationship(back_populates="chars")

    char: Mapped[str]
    preset_char_count: Mapped[int]
    typed_char_count: Mapped[int]
    avg_time_per_char: Mapped[float]
    accuracy: Mapped[float]


os.makedirs("data", exist_ok=True)

engine = create_engine("sqlite:///data/database.sqlite", echo=True)
Base.metadata.create_all(engine)


def new_session():
    return Session(engine)


# with Session(engine) as session:
#     s = Save(
#         level_progress=1,
#     )
#
#     session.add(s)
#     session.commit()
#
#     result = session.execute(select(Save))
#     print(select(Save).where(Save.level_progress == 1))
#     print(result.all())
#
#     session.execute(delete(Save))
#     session.commit()
#
# pass
