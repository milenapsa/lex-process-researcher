from app.cnj import infer_state_tribunal, normalize_cnj, validate_cnj_check_digits


def make_valid_cnj(
    seq: str = "0000001",
    year: str = "2026",
    branch: str = "8",
    court: str = "24",
    origin: str = "0001",
) -> str:
    base = int(seq + year + branch + court + origin + "00")
    dv = 98 - (base % 97)
    return f"{seq}-{dv:02d}.{year}.{branch}.{court}.{origin}"


def test_normalize_and_validate():
    value = make_valid_cnj()
    assert normalize_cnj(value) == value
    assert validate_cnj_check_digits(value) is True


def test_infer_tjsc():
    assert infer_state_tribunal(make_valid_cnj(court="24")) == "tjsc"


def test_infer_tjsp():
    assert infer_state_tribunal(make_valid_cnj(court="26")) == "tjsp"
