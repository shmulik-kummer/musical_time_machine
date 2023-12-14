import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth


# Step 1 - Scraping the Billboard Hot 100
def get_billboard_titles(date):
    # Construct the URL with the provided date
    url = f"https://www.billboard.com/charts/hot-100/{date}/"

    # Send an HTTP request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the h3 elements with the specified id and class
        title_elements = soup.find_all('h3', {'id': 'title-of-a-story',
                                              'class': 'c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only'})

        # Extract titles and save to a list
        titles = [title.text.strip() for title in title_elements]

        return titles
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None


CLIENT_ID = 'XXX'
CLIENT_SECRET = 'XXX'
REDIRECT_URI = 'http://example.com'  # This should match the redirect URI you specified in the Spotify Developer Dashboard
SCOPE = 'playlist-modify-private'


# Step 2 - Authentication with Spotify
def authenticate_spotify(client_id, client_secret, redirect_uri, scope):
    # Set up the SpotifyOAuth object
    sp_oauth = SpotifyOAuth(
        client_id,
        client_secret,
        redirect_uri,
        scope
    )

    # Get the access and refresh tokens
    token_info = sp_oauth.get_cached_token()

    # Create a Spotipy client using the obtained tokens
    spot_client = spotipy.Spotify(auth=token_info['access_token'])

    return spot_client


# Step 3 - Search Spotify for the Songs from Step 1
def get_spotify_uris(spotify_client, song_titles):
    spotify_uris = []  # List to store Spotify URIs

    for title in song_titles:
        # Search for the song on Spotify
        results = spotify_client.search(q=title, type='track', limit=1)

        # Check if any results were found
        if results['tracks']['items']:
            # Get the Spotify URI of the first result
            spotify_uri = results['tracks']['items'][0]['uri']
            spotify_uris.append(spotify_uri)
            # print(f"Found Spotify URI for '{title}': {spotify_uri}")
        else:
            print(f"No Spotify URI found for '{title}'")

    return spotify_uris


def playlist_exists(spotify_client, playlist_name):
    # Get the user's Spotify username
    user_info = spotify_client.current_user()
    user_id = user_info['id']

    # Get the user's playlists
    playlists = spotify_client.user_playlists(user_id)
    print(playlists)

    # Check if the playlist name already exists
    for existing_playlist in playlists['items']:
        existing_name = existing_playlist['name']
        print(existing_name)
        if existing_name.lower() == playlist_name.lower():
            return True

    return False


def create_billboard_playlist(spotify_client, date_str):
    # Format the date string to YYYY-MM-DD
    playlist_name = f"{date_str} Billboard 100"

    # Get the user's Spotify username
    user_info = spotify_client.current_user()
    user_id = user_info['id']

    # Create a new playlist
    new_playlist = spotify_client.user_playlist_create(user_id, playlist_name, public=False)
    print(f"Playlist '{playlist_name}' created successfully:")
    return new_playlist['id']


def add_uris_to_playlist(sp, playlist_id, uri_list):
    # Add tracks to the playlist
    sp.playlist_add_items(playlist_id=playlist_id, items=uri_list, position=None)
    print(f"Tracks added to playlist '{playlist_id}' successfully.")


# Example usage

# Get billboard 100 list titles by date
title_list = get_billboard_titles('1991-01-01')

# Authenticate in spotify
sp = authenticate_spotify(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE)

# Get spotify URI list
spotify_uris = get_spotify_uris(sp, title_list)

date_string = '1996-01-01'  # Example date
playlist = create_billboard_playlist(sp, date_string)
add_uris_to_playlist(sp, playlist, spotify_uris)
