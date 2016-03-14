from dataload import *

class AddPlaylists(object):
	def __init__(self):
		self.playlist = Playlist()

	def run(self):
		return self.playlist.addPlaylists()

if __name__ == "__main__":
	print ("Start add_playlists.py")
	
	add_playlists = AddPlaylists()
	add_playlists.run()

	print ("End add_playlists.py")
