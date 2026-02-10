from meldingen_core.statemachine import MeldingBackofficeStates, get_all_backoffice_states


def test_get_backoffice_states() -> None:
    states = get_all_backoffice_states()

    assert len(states) == 8
    assert states == [
        MeldingBackofficeStates.SUBMITTED,
        MeldingBackofficeStates.PROCESSING_REQUESTED,
        MeldingBackofficeStates.PROCESSING,
        MeldingBackofficeStates.PLANNED,
        MeldingBackofficeStates.COMPLETED,
        MeldingBackofficeStates.CANCELED,
        MeldingBackofficeStates.REOPENED,
        MeldingBackofficeStates.REOPEN_REQUESTED,
    ]
