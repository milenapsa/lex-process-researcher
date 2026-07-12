from app.registry import DATAJUD_ALIASES, TJS


def test_all_state_courts_mapped():
    assert len(TJS) == 27
    assert DATAJUD_ALIASES["tjsc"] == "api_publica_tjsc"
    assert DATAJUD_ALIASES["tjdft"] == "api_publica_tjdft"


def test_broad_datajud_coverage():
    assert len(DATAJUD_ALIASES) == 91
    assert DATAJUD_ALIASES["trf6"] == "api_publica_trf6"
    assert DATAJUD_ALIASES["trt24"] == "api_publica_trt24"
    assert DATAJUD_ALIASES["tre-sc"] == "api_publica_tre-sc"
    assert DATAJUD_ALIASES["tjmsp"] == "api_publica_tjmsp"
