'use strict';

var mongoose 	= require('mongoose'),
	Schema 		= mongoose.Schema,
	extend 		= require('extend');

var TrackSchema = new Schema({
	artist: String,
	name:  String,
	lyrics: String,
	emotion: String
});

TrackSchema.index({ emotion: 1 });

module.exports = mongoose.model('Track', TrackSchema);