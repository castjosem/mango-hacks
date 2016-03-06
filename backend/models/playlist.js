'use strict';

var mongoose 	= require('mongoose'),
	Schema 		= mongoose.Schema,
	extend 		= require('extend');

var PlaylistSchema = new Schema({
	_id: String,
	name: String,
	user_id:  String,
	personality: String,
	emotion: String,
	image: String	
});

PlaylistSchema.index({ emotion: 1 });

module.exports = mongoose.model('Playlist', PlaylistSchema);