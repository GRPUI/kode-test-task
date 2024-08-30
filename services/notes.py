from typing import List

from asyncpg import Connection
from fastapi import HTTPException

from models.notes import AddNoteModel, NoteModel, UpdateNoteModel


async def get_notes(user_id: int, connection: Connection) -> List[NoteModel]:
    """
    Функция для получения всех заметок пользователя

    :param user_id:
    :param connection:
    :return:
    """

    notes = await connection.fetch(
        """SELECT * FROM notes WHERE user_id = $1 AND is_deleted = false""", user_id
    )

    return list(map(lambda x: NoteModel(**x), notes))


async def get_note_by_id(
    note_id: int, connection: Connection, user_id: int
) -> NoteModel:
    """
    Функция для получения заметки по id

    :param user_id:
    :param note_id:
    :param connection:
    :return:
    """

    note = await connection.fetchrow(
        """SELECT * FROM notes WHERE id = $1 AND is_deleted = false""", note_id
    )

    if note["is_public"] is False and note["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return NoteModel(**note)


async def add_note(
    user_id: int, data: AddNoteModel, connection: Connection
) -> NoteModel:
    """
    Функция для добавления заметки

    :param user_id:
    :param data:
    :param connection:
    :return:
    """

    note_id = await connection.fetchval(
        """INSERT INTO notes (title, content, user_id, is_public)
        VALUES ($1, $2, $3, $4) RETURNING id;""",
        data.title,
        data.content,
        user_id,
        data.is_public,
    )

    note = await get_note_by_id(note_id, connection, user_id)

    return note


async def update_note(
    data: UpdateNoteModel, connection: Connection, user_id: int
) -> None:
    """
    Функция для обновления заметки

    :param user_id:
    :param data:
    :param connection:
    :return:
    """
    data_dict = data.dict(exclude_none=True)

    owner_id = await connection.fetchval(
        """SELECT user_id FROM notes WHERE id = $1""", data.id
    )

    if owner_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    await connection.execute(
        """UPDATE notes SET """
        + ", ".join([f"{key} = ${i + 1}" for i, key in enumerate(data_dict.keys())])
        + ", updated_at = NOW() "
        + " WHERE id = $"
        + str(len(data_dict.keys()) + 1)
        + ";",
        *data_dict.values(),
        data.id,
    )

    return


async def delete_note(note_id: int, connection: Connection, user_id: int) -> None:
    """
    Функция для удаления заметки

    :param user_id:
    :param note_id:
    :param connection:
    :return:
    """

    owner_id = await connection.fetchval(
        """SELECT user_id FROM notes WHERE id = $1""", note_id
    )

    if owner_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    await connection.execute(
        """UPDATE notes SET is_deleted = true WHERE id = $1""", note_id
    )
    return
