from typing import Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Classification:
    """This is the base model a 'classification'."""

    name: str


@dataclass
class Melding:
    """This is the base model for a 'melding'."""

    text: str
    classification: Classification | None = None
    token: str | None = None
    token_expires: datetime | None = None
    attachments: list["Attachment"] = field(default_factory=list)
    geo_location: dict[str, Any] | None = None


@dataclass
class User:
    """This is the base model for a 'user'."""

    username: str
    email: str


@dataclass
class Form:
    title: str
    classification: Classification
    questions: list["Question"]


@dataclass
class Question:
    text: str
    form: Form


@dataclass
class Answer:
    text: str
    question: Question
    melding: Melding


@dataclass
class Attachment:
    file_path: str = field(init=False)
    original_filename: str
    melding: Melding
    optimized_path: str | None = None
    thumbnail_path: str | None = None
