from typing import List

from asyncpg import Connection
from fastapi import APIRouter, Depends

from deps import DatabaseConnectionMarker
from models.notes import AddNoteModel, UpdateNoteModel, NoteModel
from services import notes
from services.users import check_access_token

router = APIRouter(dependencies=[Depends(check_access_token)])


@router.get("/")
async def get_notes(
    connection: Connection = Depends(DatabaseConnectionMarker),
    user_id: int = Depends(check_access_token),
) -> List[NoteModel]:
    return await notes.get_notes(user_id, connection)


@router.get("/{note_id}")
async def get_note_by_id(
    note_id: int,
    connection: Connection = Depends(DatabaseConnectionMarker),
    user_id: int = Depends(check_access_token),
) -> NoteModel:
    return await notes.get_note_by_id(note_id, connection, user_id)


@router.post("/add")
async def add_note(
    data: AddNoteModel,
    connection: Connection = Depends(DatabaseConnectionMarker),
    user_id: int = Depends(check_access_token),
) -> NoteModel:
    return await notes.add_note(user_id, data, connection)


@router.patch("/{note_id}", status_code=204, response_description="Note updated")
async def update_note(
    data: UpdateNoteModel,
    connection: Connection = Depends(DatabaseConnectionMarker),
    user_id: int = Depends(check_access_token),
):
    await notes.update_note(data, connection, user_id)


@router.delete("/{note_id}", status_code=204, response_description="Note deleted")
async def delete_note(
    note_id: int,
    connection: Connection = Depends(DatabaseConnectionMarker),
    user_id: int = Depends(check_access_token),
):
    await notes.delete_note(note_id, connection, user_id)
