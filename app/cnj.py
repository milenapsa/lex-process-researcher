import re


CNJ_PATTERN = re.compile(
    r"^(?P<seq>\d{7})-?(?P<dv>\d{2})\.?(?P<year>\d{4})\.?"
    r"(?P<branch>\d)\.?(?P<court>\d{2})\.?(?P<origin>\d{4})$"
)

STATE_COURT_BY_CNJ = {
    "01": "tjac", "02": "tjal", "03": "tjap", "04": "tjam", "05": "tjba",
    "06": "tjce", "07": "tjdft", "08": "tjes", "09": "tjgo", "10": "tjma",
    "11": "tjmt", "12": "tjms", "13": "tjmg", "14": "tjpa", "15": "tjpb",
    "16": "tjpr", "17": "tjpe", "18": "tjpi", "19": "tjrj", "20": "tjrn",
    "21": "tjrs", "22": "tjro", "23": "tjrr", "24": "tjsc", "25": "tjse",
    "26": "tjsp", "27": "tjto",
}


class CNJValidationError(ValueError):
    pass


def normalize_cnj(value: str) -> str:
    match = CNJ_PATTERN.fullmatch(value.strip())
    if not match:
        raise CNJValidationError("Número CNJ fora do formato esperado.")

    parts = match.groupdict()
    return (
        f"{parts['seq']}-{parts['dv']}."
        f"{parts['year']}.{parts['branch']}."
        f"{parts['court']}.{parts['origin']}"
    )


def cnj_digits(value: str) -> str:
    return re.sub(r"\D", "", normalize_cnj(value))


def validate_cnj_check_digits(value: str) -> bool:
    digits = cnj_digits(value)
    seq = digits[0:7]
    dv = digits[7:9]
    year = digits[9:13]
    branch = digits[13:14]
    court = digits[14:16]
    origin = digits[16:20]
    base = int(seq + year + branch + court + origin + "00")
    expected = 98 - (base % 97)
    return int(dv) == expected


def infer_state_tribunal(value: str) -> str | None:
    digits = cnj_digits(value)
    branch = digits[13:14]
    court = digits[14:16]
    if branch != "8":
        return None
    return STATE_COURT_BY_CNJ.get(court)
