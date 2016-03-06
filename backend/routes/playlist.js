var express 		= require('express');
var router 			= express.Router();
var Promise 		= require('bluebird');
var Playlist 		= require('./../models/playlist');



router.post('/api/playlist', function(request, response, next){
	var id = request.body.id;
	var playlist = new Playlist({ _id: id});
	playlist.name 			= request.body.name;
	playlist.user_id 		= request.body.user_id;
	playlist.personality 	= request.body.personality;
	playlist.emotion 		= request.body.emotion;
	playlist.image 			= request.body.image;

	playlist.save(function(err){
		if(err)
			response.send(err);
		response.json("Playlist created!");
	});
});


module.exports = router;