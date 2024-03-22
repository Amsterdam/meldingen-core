from dataclasses import dataclass


@dataclass
class Classification:
    """This is the base model a 'classification'."""

    name: str


@dataclass
class Melding:
    """This is the base model for a 'melding'."""

    text: str
    classification: Classification | None = None


@dataclass
class User:
    """This is the base model for a 'user'."""

    username: str
    email: str


@dataclass
class Question:
    text: str
    classification: Classification


@dataclass
class Answer:
    text: str
    question: Question
    melding: Melding
