from meldingen_core.statemachine import MeldingBackofficeStates, get_all_backoffice_states


def test_get_backoffice_states() -> None:
    states = get_all_backoffice_states()

    assert len(states) == 3
    assert states == [
        MeldingBackofficeStates.SUBMITTED,
        MeldingBackofficeStates.PROCESSING,
        MeldingBackofficeStates.COMPLETED,
    ]
