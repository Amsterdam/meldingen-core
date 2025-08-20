from dataclasses import dataclass
from typing import List

from meldingen_core.statemachine import MeldingStates


@dataclass
class MeldingListFilters:
    area: str | None = None
    states: List[MeldingStates] | None = None
