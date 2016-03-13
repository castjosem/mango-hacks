# -*- coding: utf-8 -*-
import os
import json
import requests
import string
import re
import spotipy
import spotipy.util as util
from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session, exceptions

from pprint import pprint
from json import JSONDecodeError
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials


script_dir = os.path.dirname(__file__)

#serverUrl = 'http://127.0.0.1:3000'

serverUrl = 'http://45.55.105.121:3000'

class EchonestAPI(object):
	def __init__(self):
		self.baseUrl = "http://developer.echonest.com/api/v4/song/search"
		self.payload = {
			"api_key": "Y01VDKCQNCP2RDYSP",
			"sort": "song_hotttnesss-desc",
			"bucket": "song_hotttnesss",
			"bucket": "artist_hotttnesss",
			"mood": "",
			"results": "100"
		};	
		self.emotions = set(["happy", "angry", "sad", "relaxing", "excited"])
		self.session = requests.Session()
		self.adapters = requests.adapters.HTTPAdapter(max_retries=10)

	def get_lyricsUrl(self, mood=""):
		if mood in self.emotions:
			self.payload["mood"] = mood
			return self.session.get(self.baseUrl, params=self.payload, timeout=5)
		else:
			return None


class MusixMatchAPI(object):
	def __init__(self):
		#"apikey": "0bcd220b9ee2b77e21cf75a8456dc98a",
		self.baseUrl = "http://api.musixmatch.com/ws/1.1/matcher.track.get";
		self.payload = {
			"apikey": "c76f219813a9c40ed549724c6ba8c3fa",
			"f_has_lyrics": 1,
			"q_track": "",
			"q_artist": "",
			"format": "json",
		};
		self.session = requests.Session()
		self.adapters = requests.adapters.HTTPAdapter(max_retries=10)

	def get_lyricsUrl(self, name="", artist=""):
		self.payload['q_track'] = name
		self.payload['q_artist'] = artist
		return self.session.get(self.baseUrl, params=self.payload, timeout=5)

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
		self.mmatch_api = MusixMatchAPI()

	def loadEmotions(self):
		headers = {
			'Host': 'www.musixmatch.com:443',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Encoding': 'gzip, deflate, sdch',
			'Accept-Language': 'en',
			'Cookie': 'returning=11; musixmatchUserGuid=b1f6f4c4-3995-4a01-925d-badc2d02d3de; fbm_131314396964274=base_domain=.musixmatch.com; ARRAffinity=f3809c8ad5cdbf9b9f12190dd515fdef3b8bbddf9bcfa41dfd953eef09528b7d; captcha_id=nJIYx28QZH80RsCVdteh4TjT8jqeuBtZeIdox2UUNkl20SmbjNKPMKKXjuErmUtKH5jmRTIcbTg%3D; accountProviderUserToken=ya29.pAK-62NoGFyMQHbSpKd97wuvkzX7qZX5to9l6bzdplWeQX8pcycUxdNOc5H0p503oA; accountProviderName=google; musixmatchUserToken=16031370690c9f053f7e8b632b814ae5140a29d2a45d439ebdfcde; userInfo=%7B%22id%22%3A%22107986471538769477073%22%2C%22name%22%3A%22Jose%20Castillo%22%2C%22firstName%22%3A%22Jose%22%2C%22lastName%22%3A%22Castillo%22%2C%22photo%22%3A%22//lh4.googleusercontent.com/-p7CI4gSHirQ/AAAAAAAAAAI/AAAAAAAAABY/k0h1dZ2FHWc/photo.jpg%3Fsz%3D50%22%7D; userLoggedin=true; ARRAffinity=65a6815cef8b359738f0ae3a11e7126c0de85cb2b70f244f0b52734cf6daf8a7; returning=17; _gat=1; AWSELB=5787A55B12CDBC6648FF265BE60F391D6FCA7C791E7FD36024D83983716F0D2A83D82470EFA97D8A8ACA55130082EFD075470556DF11839918ED530A4FB609B352481EFB2E; _ga=GA1.2.169313919.1457169111; x-mxm-user-id=g2%3A107986471538769477073; x-mxm-token-guid=b1f6f4c4-3995-4a01-925d-badc2d02d3de; mxm-encrypted-token=oL51rYspmbSjZGJsV5Q8W%2BU%2FpOXGxpMy6dmL1Ik2DoA%2FUFNrm1Kw%2Fww4DtPOqD9SF%2Ffai32eLbD4TOlPDebPlRVq7AOugupLCgZ%2BWVJdICMHB6hZqouPbSmwE7oemYsbiJ6cg6TYT0XYTKdCKDkjyglHaZAi126bfJOz6bpoeyDI57G6EBcznMKOFUgZywpqDVb40a2odSXjFYtUl5PKGxCp%2FzKZ2oz274SjpqP6urJEJyZtUL3Lf%2B8Sy65zDSX5N7GY9h5DfGh0fr3c5GvHphPBvEipfsfoJ0YbPY%2BLn3RTvT9p8tIcf1yplCVGU%2BVK9HIJfth3LbCq57M21N1yMSlXX5ZG%2F39an1kEUc%2BYOzINh91PZafL8WfW3GiC8DK7wQdYmg2XAHHHiJ2s39XrdUWhrwpvDViwFmyO9chA3o9m2%2FnAE8DIMRakT9hEq4xWeAOcDhpcVN14ckqTYgU6Hw3QN5Fjtl8OrBWhN2aAWAqNuyjl5Z1UlRczEy%2F0qe%2FzsHZ7s%2BSD4ScHZZVyKg8QyJXHChDvSPAEZwn0zyVYlu7XoexInq5HsEHI4nx977knain4laTbpOAKnbusGdOpPA%3D%3D',
			'Upgrade-Insecure-Requests': '1,',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
		}

		with open(os.path.join(script_dir, '..', 'data', 'training_data.json'), 'r', encoding="utf8") as data_file:    
			data = json.load(data_file)

			for i, track in enumerate(data):
				song = track['song']
				artist = track['artist']
				emotion = track['emotion']
				try:
					mm_lyrics = self.mmatch_api.get_lyricsUrl(song, artist)
					if mm_lyrics.status_code == 200:

						mm_lyrics = mm_lyrics.text
						json_text = re.sub(r'\\(.)', r'\1', mm_lyrics)

						mm_lyrics = json.loads(json_text)
						
						#print(json.dumps(mm_lyrics, sort_keys=True, indent=4))


						if mm_lyrics and mm_lyrics['message']['body']['track']:
							lyrics_url = mm_lyrics['message']['body']['track']['track_share_url']
							page = requests.get(lyrics_url, headers=headers, timeout=5)
							data = page.text
							soup = BeautifulSoup(data, "html.parser")
							lyrics = soup.find("div", {"class":"body",  "id": "selectable-lyrics"})
							lyrics = lyrics.text
							
							if lyrics is not None and len(lyrics) > 0:
								resp = requests.post(serverUrl + '/api/emotion/load', json = {'lyrics': lyrics, 'emotion': emotion, 'artist': artist, 'name': song })
								print (resp.text)

				except TypeError:
					print ("Error", song, artist)

				except ValueError:
					print ("Error", song, artist)

				except UnicodeEncodeError:
					print ("Error", song, artist)

				except JSONDecodeError:
					print ("Error", song, artist)



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
					mm_lyrics = self.mmatch_api.get_lyricsUrl(track_name, track_album)
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
	playlist.loadEmotions()
	print ("End data loader")


