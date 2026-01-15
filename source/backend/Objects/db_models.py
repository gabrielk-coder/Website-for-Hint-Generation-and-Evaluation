from __future__ import annotations
import json
from typing import Any, Dict, Optional, List
import sqlite3
from pydantic import BaseModel, Field, ConfigDict 



def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# ---------------------------------------------------------------------
# Pydantic models mirroring the DB tables
# ---------------------------------------------------------------------

class DBBaseModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())


class QuestionOBJ(DBBaseModel):
    """
    Represents a row in the `questions` table.
    """
    id: Optional[int] = Field(default=None)
    text: str
    session_id: Optional[str] = None
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "QuestionOBJ":
        return cls(
            id=row["id"],
            text=row["text"],
            session_id=row["session_id"],
            created_at=row["created_at"],
        )


class AnswerOBJ(DBBaseModel):
    """
    Represents a row in the `answers` table.
    """
    id: Optional[int] = Field(default=None)
    question_id: int
    answer_text: str
    model_name: Optional[str] = None 
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "AnswerOBJ":
        return cls(
            id=row["id"],
            question_id=row["question_id"],
            answer_text=row["answer_text"],
            model_name=row["model_name"],
            created_at=row["created_at"],
        )


class HintOBJ(DBBaseModel):
    """
    Represents a row in the `hints` table.
    """
    id: Optional[int] = Field(default=None)
    question_id: int
    answer_id: Optional[int] = None
    hint_text: str
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "HintOBJ":
        return cls(
            id=row["id"],
            question_id=row["question_id"],
            answer_id=row["answer_id"],
            hint_text=row["hint_text"],
            created_at=row["created_at"],
        )


class MetricOBJ(DBBaseModel):
    """
    Represents a row in the `metrics` table.
    `metadata_json` is exposed as a dict `metadata`.
    """
    id: Optional[int] = Field(default=None)
    hint_id: int
    name: str
    value: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "MetricOBJ":
        raw = row["metadata_json"]
        metadata = json.loads(raw) if raw else {}
        return cls(
            id=row["id"],
            hint_id=row["hint_id"],
            name=row["name"],
            value=row["value"],
            metadata=metadata,
        )

    def to_db_tuple(self) -> tuple:
        """
        Helper for INSERT:
        (hint_id, name, value, metadata_json)
        """
        return (
            self.hint_id,
            self.name,
            self.value,
            json.dumps(self.metadata, ensure_ascii=False),
        )


class EntityOBJ(DBBaseModel):
    """
    Represents a row in the `entities` table.
    `metadata_json` is exposed as a dict `metadata`.
    """
    id: Optional[int] = Field(default=None)
    hint_id: int
    entity: Optional[str] = None
    ent_type: Optional[str] = None
    start_index: Optional[int] = None
    end_index: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "EntityOBJ":
        raw = row["metadata_json"]
        metadata = json.loads(raw) if raw else {}
        return cls(
            id=row["id"],
            hint_id=row["hint_id"],
            entity=row["entity"],
            ent_type=row["ent_type"],
            start_index=row["start_index"],
            end_index=row["end_index"],
            metadata=metadata,
        )

    def to_db_tuple(self) -> tuple:
        """
        Helper for INSERT:
        (hint_id, entity, ent_type, start_index, end_index, metadata_json)
        """
        return (
            self.hint_id,
            self.entity,
            self.ent_type,
            self.start_index,
            self.end_index,
            json.dumps(self.metadata, ensure_ascii=False),
        )


class CandidateAnswerOBJ(DBBaseModel):
    """
    Represents a row in the `candidate_answers` table.
    """
    id: Optional[int] = Field(default=None)
    question_id: int
    candidate_text: str
    is_eliminated: bool = False
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "CandidateAnswerOBJ":
        return cls(
            id=row["id"],
            question_id=row["question_id"],
            candidate_text=row["candidate_text"],
            is_eliminated=bool(row["is_eliminated"]),
            created_at=row["created_at"],
        )