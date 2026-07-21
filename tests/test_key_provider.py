from app.key_provider import DataJudKeyProvider


def test_extract_key_from_plain_text():
    html = "Authorization: APIKey abcdefghijklmnopqrstuvwxyz0123456789=="
    assert (
        DataJudKeyProvider.extract_key(html)
        == "abcdefghijklmnopqrstuvwxyz0123456789=="
    )


def test_extract_key_from_current_official_html_shape():
    html = """
    <section>
      <h2>API Key</h2>
      <ul>
        <li>APIKey atual:
          <ul>
            <li><span>Authorization:</span> <strong>APIKey</strong>
              <code>cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==</code>
            </li>
          </ul>
        </li>
      </ul>
    </section>
    """
    assert (
        DataJudKeyProvider.extract_key(html)
        == "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
    )


def test_extract_key_returns_none_without_marker():
    assert DataJudKeyProvider.extract_key("<p>sem chave</p>") is None
