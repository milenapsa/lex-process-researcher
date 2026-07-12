from app.key_provider import DataJudKeyProvider


def test_extract_official_key_format():
    html = """
    <p>Authorization: APIKey abcDEF123_-/+=abcDEF123_-/+=</p>
    """
    assert DataJudKeyProvider.extract_key(html) == "abcDEF123_-/+=abcDEF123_-/+="


def test_rejects_unrelated_text():
    assert DataJudKeyProvider.extract_key("<p>sem chave</p>") is None
