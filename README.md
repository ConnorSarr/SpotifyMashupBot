# SpotifyMashupBot
A program that utilizes Spotify's API to suggest mashup ideas based on BPMs and keys of songs found in a Spotify playlist

## Installation
- ```pip install -r requirements.txt```
- Make an application using Spotify's developer portal. Then paste the client ID and client secret in the following code block found in the main.py file:

```sh
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="YOUR_CLIENT_ID",
                                               client_secret="YOUR_CLIENT_SECRET",
                                               redirect_uri="https://localhost/",
                                               scope="user-library-read",
                                               open_browser=True)) #setup the Spotify app
```
