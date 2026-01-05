from meldingen_core.statemachine import MeldingBackofficeStates, get_all_backoffice_states


def test_get_backoffice_states() -> None:
    states = get_all_backoffice_states()

    assert len(states) == 8
    assert states == [
        MeldingBackofficeStates.SUBMITTED,
        MeldingBackofficeStates.AWAITING_PROCESSING,
        MeldingBackofficeStates.PROCESSING,
        MeldingBackofficeStates.PLANNED,
        MeldingBackofficeStates.COMPLETED,
        MeldingBackofficeStates.CANCELED,
        MeldingBackofficeStates.REOPENED,
        MeldingBackofficeStates.REOPEN_REQUESTED,
    ]
