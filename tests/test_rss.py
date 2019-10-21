
def test_get_rss_files_from_URL(client, app):
    response = client.get("/feed.rss")
    assert b"<rss " in response.data
    assert b"<channel>" in response.data
    assert b"test title" in response.data
