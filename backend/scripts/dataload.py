# -*- coding: utf-8 -*-
import os
import json
import requests
import string
import re
import sys
import spotipy
import spotipy.util as util
from requests.packages.urllib3.util import Retry
from requests.packages.urllib3.exceptions import *
from requests.adapters import HTTPAdapter
from requests import Session, exceptions

from pprint import pprint
from json import JSONDecodeError
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials

class Config(object):
	serverUrl = 'http://45.55.105.121:3000'

	@staticmethod
	def server_url():
		return Config.serverUrl


class WebSrapping(object):
	def __init__(self):
		self.headers = {
			'Host': 'www.musixmatch.com:443',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Encoding': 'gzip, deflate, sdch',
			'Accept-Language': 'en',
			'Cookie': 'musixmatchUserGuid=aff0bca2-2f28-407a-a114-27d0555a5e1d; ARRAffinity=a01e98d8bf095bd5e8f875e38089ea77e17132fe3a70f80085d7b331a2f4b4e3; captcha_id=3RJ3FiayvxuZz2K%2B6YlVeDePxeQ2Sy7OjyuC43RLCSXdjbvY7kNn1wlTLiBytkVkdOLH9VzePRE%3D; x-mxm-user-id=undefined; x-mxm-token-guid=undefined; AWSELB=5787A55B12CDBC6648FF265BE60F391D6FCA7C791E91744265B599ED339B08120FEE30807C907613FEBA554EDFFB1EF49CD38BD3234A7D9D18024133A75A2EAA7611C04F82',
			'Upgrade-Insecure-Requests': '1,',
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
		}

	def getPage(self, url):
		self.session = requests.Session()
		self.adapters = requests.adapters.HTTPAdapter(max_retries=10)
		return self.session.get(url, headers=self.headers, timeout=5)

	def getLyrics(self, lyrics_url):
		page = self.getPage(lyrics_url)
		data = page.text
		soup = BeautifulSoup(data, "html.parser")
		lyrics = soup.find("div", {"class":"body",  "id": "selectable-lyrics"})
		if lyrics:
			return lyrics.text
		return None


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
			return self.session.get(self.baseUrl, params=self.payload, timeout=10)
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
			"q_album": "",
			"format": "json",
		};		
		self.w_scrapping = WebSrapping()

	def getLyricsUrl(self, name="", artist="", album=""):
		self.payload['q_track'] = name
		self.payload['q_artist'] = artist
		self.payload['q_album'] = album

		self.session = requests.Session()
		self.adapters = requests.adapters.HTTPAdapter(max_retries=10)
		return self.session.get(self.baseUrl, params=self.payload, timeout=10)

	def getLyrics(self, song=None, artist=None, album=""):
		if not song or not artist: return None

		try:
			mm_lyrics = self.getLyricsUrl(song, artist)
			if mm_lyrics.status_code == 200:
				mm_lyrics = mm_lyrics.text
				json_text = re.sub(r'\\(.)', r'\1', mm_lyrics)
				mm_lyrics = json.loads(json_text)

				if mm_lyrics and mm_lyrics['message']['body'] and mm_lyrics['message']['body']['track']:
					lyrics_url = mm_lyrics['message']['body']['track']['track_share_url']
					print (lyrics_url)

					lyrics = self.w_scrapping.getLyrics(lyrics_url)
					return lyrics
		except ReadTimeoutError:
			print ("Timeout error", song, artist, album)
		except ConnectionRefusedError:
			print ("ConnectionRefused error", song, artist, album)
		except NewConnectionError:
			print ("ConnectionRefused error", song, artist, album)
		return None




class SpotifyAPI(object):
	client_id = "b79258f909ea42b1aff83840ccb1b03c"
	client_secret = "a513642b701948648e303403fda73c04"

	def __init__(self):
		oauth = SpotifyClientCredentials(self.client_id, self.client_secret)
		token = oauth.get_access_token()
		self.sp = spotipy.Spotify(auth=token)

	def featured_playlists(self):
		return self.sp.featured_playlists(limit=50)

	def track_info(self, user_id, playlist_id):
		return self.sp.user_playlist_tracks(user_id, playlist_id=playlist_id, fields="items(track(name, artists(name), album(name)))", limit=25, offset=0)



class Classifier(object):
	def __init__(self):
		self.mmatch_api = MusixMatchAPI()
		self.w_scrapping = WebSrapping()

	def train(self, file_path = None):
		if not file_path: return (False, "Error in file name")

		with open(file_path, 'r', encoding="utf8") as data_file:    
			data = json.load(data_file)

			print ("Start")
			for i, track in enumerate(data):
				song = track['song']
				artist = track['artist']
				emotion = track['emotion']
				try:
					lyrics = self.mmatch_api.getLyrics(song, artist)
							
					if lyrics is not None and len(lyrics) > 0:
						resp = requests.post(Config.server_url() + '/api/emotion/load', json = {'lyrics': lyrics, 'emotion': emotion, 'artist': artist, 'name': song })
						print (resp.text)
					else:
						print ("Lyrics not found: ", song, artist)

				except TypeError:
					print ("Error", song, artist)

				except ValueError:
					print ("Error", song, artist)

				except UnicodeEncodeError:
					print ("Error", song, artist)

				except JSONDecodeError:
					print ("Error", song, artist)
		
		return (True, "Successful")



class Playlist(object):
	def __init__(self):
		self.sp_api = SpotifyAPI()
		self.mmatch_api = MusixMatchAPI()
		self.w_scrapping = WebSrapping()

	def addPlaylists(self):	
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
				song = str(track['track']['name'])
				song.replace('(', ' ');
				song.replace(')', ' ');

				album =  track['track']['album']['name']
				artist = ""
				if track['track']['artists']:
					artists = track['track']['artists']
					if artists and len(artists) > 0:
						artist = artists[0]['name']

				try:					
					lyrics = self.mmatch_api.getLyrics(song, artist, album)
					if lyrics is not None and len(lyrics) > 0:
						total_lyrics.append(lyrics)
					else:
						print ("Lyrics not found: %s,    %s,     %s" % (song, artist, album))

				except TypeError as err:
					print ("Error: %s,    %s,    %s,    %s" % (song, artist, album, err))

				except ValueError as err:
					print ("Error: %s,    %s,    %s,    %s" % (song, artist, album, err))

				except UnicodeEncodeError as err:
					print ("Error: %s,    %s,    %s,    %s" % (song, artist, album, err))

				except JSONDecodeError as err:
					print ("Error: %s,    %s,    %s,    %s" % (song, artist, album, err))


			lyrics = "".join(total_lyrics)
			print ("Lyrics #: %s ,         %s" % (len(lyrics), playlist_url))

			if lyrics is not None and len(lyrics) > 0:
				try:
					personality_resp = requests.post(Config.server_url() + '/api/personality/analyze', json = {'text': lyrics})
					emotion_resp = requests.post(Config.server_url() + '/api/emotion/track', json = {'lyrics': lyrics})

					personality_resp = personality_resp.json()
					personality = personality_resp['personality']
					emotion_resp = emotion_resp.json()
					emotion = emotion_resp['emotion']

					resp = requests.post(	Config.server_url() + '/api/playlist', 
											json = {
												'id': playlist_id, 
												'name': playlist_name, 
												'user_id': user_id,
												'personality': personality, 
												'emotion': emotion, 
												'image': playlist_image
											})
					print (resp.text)
				except Exception as err:
					print (err)
				except:
					print ("Error inserting to server. Unknown")

