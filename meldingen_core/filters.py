from dataclasses import dataclass
from typing import List

from meldingen_core.statemachine import BaseMeldingState


@dataclass
class MeldingListFilters:
    area: str | None = None
    states: List[BaseMeldingState] | None = None
