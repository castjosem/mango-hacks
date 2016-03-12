# -*- coding: utf-8 -*-
import json
import requests
import string
import spotipy
import spotipy.util as util
from json import JSONDecodeError
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials


#serverUrl = 'http://127.0.0.1:3000'

serverUrl = 'http://45.55.105.121:3000'

class LyricsAPI(object):
	def __init__(self):
		self.baseUrl = "https://www.musixmatch.com/ws/1.1/macro.search"
		self.headers = {'Content-Type': 'application/json'}
		self.payload = {
			'app_id': 'community-app-v1.0', 
			'guid': 'b1f6f4c4-3995-4a01-925d-badc2d02d3de',
			'format': 'json',
			'page_size': '1',
			'part': 'artist_image',
			'q': ''
		}

	def get_lyrics(self, name="", artist=""):
		self.payload['q'] = name + ' ' + artist
		return requests.get(self.baseUrl, params=self.payload, headers=self.headers)

class SpotifyAPI(object):
	client_id = "b79258f909ea42b1aff83840ccb1b03c"
	client_secret = "a513642b701948648e303403fda73c04"

	def __init__(self):
		oauth = SpotifyClientCredentials(self.client_id, self.client_secret)
		token = oauth.get_access_token()
		self.sp = spotipy.Spotify(auth=token)

	def featured_playlists(self):
		return self.sp.featured_playlists(limit=10)

	def track_info(self, user_id, playlist_id):
		return self.sp.user_playlist_tracks(user_id, playlist_id=playlist_id, fields="items(track(name, album(name)))", limit=15, offset=0)



class Playlist(object):	
	bad_chars = '(){}<>'

	def __init__(self):
		self.sp_api = SpotifyAPI()
		self.lyrics_api = LyricsAPI()

	def updateTracks(self):		
		results = self.sp_api.featured_playlists()
		
		playlists = results["playlists"]
		for i, item in enumerate(playlists['items']):
			total_lyrics = []

			playlist_name = item['name']
			playlist_url = item['href']
			playlist_id = item['id']
			playlist_image = item['images'][0]['url'] if item['images'] else ""
			user_id = item['owner']['id']

			tracks = self.sp_api.track_info(user_id, playlist_id)

			for j, track in enumerate(tracks['items']):
				track_name = str(track['track']['name'])
				track_name.replace('(', ' ');
				track_name.replace(')', ' ');
				track_album =  track['track']['album']['name']

				try:
					mm_lyrics = self.lyrics_api.get_lyrics(track_name, track_album)
					mm_lyrics = mm_lyrics.json()

					if not mm_lyrics['message']['body']['macro_result_list']['track_list']: continue					
					lyrics_url = mm_lyrics['message']['body']['macro_result_list']['track_list'][0]['track']['track_share_url']
					
					page = requests.get(lyrics_url)
					data = page.text
					soup = BeautifulSoup(data, "html.parser")
					lyrics = soup.find("div", {"class":"body",  "id": "selectable-lyrics"})
					if lyrics is None: continue
					total_lyrics.append(lyrics.get_text())

				except UnicodeEncodeError:
					pass

				except JSONDecodeError:
					pass


			result_lyrics = "".join(total_lyrics)
			playlist_pi = requests.post(serverUrl + '/api/analyze', json = {'text': result_lyrics})
			personality = playlist_pi.json()



			requests.post(serverUrl + '/api/playlist', 
				json = {
					'id': playlist_id,
					'name': playlist_name,
					'user_id': user_id,
					'personality': personality['personality'],
					'emotion': personality['emotion']['tone_name'],
					'image': playlist_image
				})


if __name__ == "__main__":
	playlist = Playlist()
	playlist.updateTracks()
	print ("End data loader")
