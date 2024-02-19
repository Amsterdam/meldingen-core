class Classification:
    """This is the base model a 'classification'."""
    name: str


class Melding:
    """This is the base model for a 'melding'."""

    text: str
    classification: Classification | None = None


class User:
    """This is the base model for a 'user'."""

    username: str
    email: str
