from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Classification:
    """This is the base model for a 'classification'."""

    name: str


@dataclass
class Melding:
    """This is the base model for a 'melding'."""

    text: str
    classification: Classification | None = None
    attachments: Sequence["Attachment"] = field(default_factory=list)
    token: str | None = None
    token_expires: datetime | None = None
    street: str | None = None
    house_number: int | None = None
    house_number_addition: str | None = None
    postal_code: str | None = None
    city: str | None = None
    email: str | None = None
    phone: str | None = None
    state: str | None = None


@dataclass
class User:
    """This is the base model for a 'user'."""

    username: str
    email: str


@dataclass
class Form:
    title: str
    classification: Classification
    questions: Sequence["Question"]


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
    original_media_type: str
    melding: Melding
    optimized_path: str | None = None
    optimized_media_type: str | None = None
    thumbnail_path: str | None = None
    thumbnail_media_type: str | None = None
