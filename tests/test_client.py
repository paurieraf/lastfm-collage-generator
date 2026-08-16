from unittest.mock import patch, MagicMock
from lastfmcollagegenerator.lastfm.client import LastfmClient


@patch("lastfmcollagegenerator.lastfm.client.pylast.LastFMNetwork")
def test_lastfm_client_initialization_and_methods(mock_network_cls):
    mock_network = MagicMock()
    mock_network_cls.return_value = mock_network

    client = LastfmClient(api_key="key123", api_secret="secret123")
    mock_network_cls.assert_called_once_with(api_key="key123", api_secret="secret123")

    mock_user = MagicMock()
    mock_network.get_user.return_value = mock_user

    # Test get_user
    user = client.get_user("testuser")
    assert user == mock_user
    mock_network.get_user.assert_called_once_with("testuser")

    # Test get_top_albums
    mock_user.get_top_albums.return_value = ["mock_album"]
    albums = client.get_top_albums(mock_user, limit=5, period="7day")
    assert albums == ["mock_album"]
    mock_user.get_top_albums.assert_called_once_with(period="7day", limit=5)

    # Test get_top_artists
    mock_user.get_top_artists.return_value = ["mock_artist"]
    artists = client.get_top_artists(mock_user, limit=3, period="1month")
    assert artists == ["mock_artist"]
    mock_user.get_top_artists.assert_called_once_with(period="1month", limit=3)

    # Test get_top_tracks
    mock_user.get_top_tracks.return_value = ["mock_track"]
    tracks = client.get_top_tracks(mock_user, limit=10, period="overall")
    assert tracks == ["mock_track"]
    mock_user.get_top_tracks.assert_called_once_with(period="overall", limit=10)
