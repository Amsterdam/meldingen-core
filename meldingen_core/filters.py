from dataclasses import dataclass
from typing import Sequence

from meldingen_core.statemachine import BaseMeldingState


@dataclass
class MeldingListFilters:
    area: str | None = None
    states: Sequence[BaseMeldingState] | None = None
