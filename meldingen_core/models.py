from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, MutableSequence


@dataclass
class AssetType:
    name: str
    class_name: str
    arguments: dict[str, Any]


@dataclass
class Classification:
    name: str
    asset_type: AssetType | None = None


@dataclass
class Melding:
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
    assets: MutableSequence["Asset"] = field(default_factory=list)


@dataclass
class Asset:
    external_id: str
    type: AssetType
    melding: Melding


@dataclass
class User:
    """This is the base model for a 'user'."""

    username: str
    email: str


@dataclass
class Form:
    title: str
    questions: Sequence["Question"]
    classification: Classification | None = None


@dataclass
class Question:
    text: str
    form: Form | None = None


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
