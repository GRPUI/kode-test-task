import datetime
from typing import List

from pydantic import BaseModel


class AddNoteModel(BaseModel):
    """Модель для создания заметки

    Атрибуты:

    title: str -- заголовок заметки;
    content: str -- содержимое заметки;
    is_public: bool -- флаг публичности заметки.
    """

    title: str
    content: str
    is_public: bool = False


class NoteModel(BaseModel):
    """Модель для заметки

    Атрибуты:

    id: int -- идентификатор заметки;
    title: str -- заголовок заметки;
    content: str -- содержимое заметки;
    user_id: int -- идентификатор пользователя;
    is_public: bool -- флаг публичности заметки;
    is_deleted: bool -- флаг удаления заметки;
    created_at: datetime.datetime | str -- дата создания заметки;
    updated_at: datetime.datetime | str -- дата последнего обновления заметки.
    """

    id: int
    title: str
    content: str
    user_id: int
    is_public: bool
    is_deleted: bool
    created_at: datetime.datetime | str = datetime.datetime.now()
    updated_at: datetime.datetime | str = datetime.datetime.now()


class NoteModelWithMisspellings(NoteModel):
    """Модель для заметки с опечатками

    Атрибуты:

    id: int -- идентификатор заметки;
    title: str -- заголовок заметки;
    content: str -- содержимое заметки;
    user_id: int -- идентификатор пользователя;
    is_public: bool -- флаг публичности заметки;
    is_deleted: bool -- флаг удаления заметки;
    created_at: datetime.datetime | str -- дата создания заметки;
    updated_at: datetime.datetime | str -- дата последнего обновления заметки.
    misspellings: list -- список опечаток в заметке.
    """

    misspellings: List


class UpdateNoteModel(BaseModel):
    """Модель для обновления заметки

    Атрибуты:

    id: int -- идентификатор заметки;
    title: str -- заголовок заметки;
    content: str -- содержимое заметки;
    is_public: bool -- флаг публичности заметки;
    """

    id: int
    title: str = None
    content: str = None
    is_public: bool = None
