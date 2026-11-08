from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import SavedProgram, User
from app.schemas.schemas import (
    SavedProgramCreate, SavedProgramUpdate,
    SavedProgramOut, WorkspaceRunRequest, WorkspaceRunResult,
)
from app.routers.auth import get_current_user
from app.services.code_runner import CodeRunner

router = APIRouter(prefix="/api/workspace", tags=["workspace"])
_runner = CodeRunner()


@router.get("/programs", response_model=List[SavedProgramOut])
def list_saved_programs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all saved Python programs belonging to the logged-in student."""
    return (
        db.query(SavedProgram)
        .filter(SavedProgram.user_id == current_user.id)
        .order_by(SavedProgram.updated_at.desc())
        .all()
    )


@router.post("/programs", response_model=SavedProgramOut, status_code=201)
def create_saved_program(
    data: SavedProgramCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a new code file / web project to the student's personal library."""
    title = data.title.strip() or "Untitled Program"
    program = SavedProgram(
        user_id=current_user.id,
        title=title,
        description=data.description or "",
        language=data.language or "python",
        code=data.code,
        extra_data=data.extra_data,
    )
    db.add(program)
    db.commit()
    db.refresh(program)
    return program


@router.get("/programs/{program_id}", response_model=SavedProgramOut)
def get_saved_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Load a specific saved program."""
    program = (
        db.query(SavedProgram)
        .filter(SavedProgram.id == program_id, SavedProgram.user_id == current_user.id)
        .first()
    )
    if not program:
        raise HTTPException(status_code=404, detail="Saved program not found")
    return program


@router.put("/programs/{program_id}", response_model=SavedProgramOut)
def update_saved_program(
    program_id: int,
    data: SavedProgramUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update title, description, language, or code of an existing program."""
    program = (
        db.query(SavedProgram)
        .filter(SavedProgram.id == program_id, SavedProgram.user_id == current_user.id)
        .first()
    )
    if not program:
        raise HTTPException(status_code=404, detail="Saved program not found")

    if data.title is not None:
        program.title = data.title.strip() or program.title
    if data.description is not None:
        program.description = data.description
    if data.language is not None:
        program.language = data.language
    if data.code is not None:
        program.code = data.code
    if data.extra_data is not None:
        program.extra_data = data.extra_data

    db.commit()
    db.refresh(program)
    return program


@router.delete("/programs/{program_id}")
def delete_saved_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a saved program from the student's library."""
    program = (
        db.query(SavedProgram)
        .filter(SavedProgram.id == program_id, SavedProgram.user_id == current_user.id)
        .first()
    )
    if not program:
        raise HTTPException(status_code=404, detail="Saved program not found")

    db.delete(program)
    db.commit()
    return {"success": True, "message": "Program deleted"}


@router.post("/run", response_model=WorkspaceRunResult)
def run_workspace_code(
    payload: WorkspaceRunRequest,
    current_user: User = Depends(get_current_user),
):
    """Execute arbitrary Python code in the sandbox playground."""
    result = _runner.run_custom_script(payload.code, payload.stdin_input or "")
    return result
