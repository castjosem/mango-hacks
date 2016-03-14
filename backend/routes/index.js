var express 		= require('express');
var	config  		= require('./../config/config');
var util 			= require('./../util/utilities');
var Playlist 		= require('./../models/playlist');
var Track 			= require('./../models/track');
var router 			= express.Router();
var Promise 		= require('bluebird');
var mongoose 		= Promise.promisifyAll(require('mongoose'));
var watson 			= require('watson-developer-cloud');
var tone_analyzer 	= new watson.tone_analyzer(config.services.tone_analyzer);
var twitter_config 	= config.api.twitter;
var Twit 			= Promise.promisifyAll(require('twit'));
var pi_threshold 	= config.pi_threshold;

var T = new Twit({
	consumer_key:         twitter_config.consumer_key,
	consumer_secret:      twitter_config.consumer_secret,
	access_token:         twitter_config.access_token,
	access_token_secret:  twitter_config.access_token_secret,
	timeout_ms:           60*1000
});


var classifier 		= require('./../modules/classifier');


router.get('/', function(req, res, next) {
	res.render('index', { title: 'Express' });
});



router.post('/api/playlist/search', function(request, response, next){
	if (typeof request.body.username !== 'undefined' && typeof request.body.emotion !== 'undefined'){
		var username = request.body.username;
		var emotion = request.body.emotion;
		
		var options = { screen_name: username,  count: twitter_config.count };
		var tweets = [];

		T.get('statuses/user_timeline', options , function(err, data) {
			for (var i = 0; i < data.length ; i++) {
				tweets.push(data[i].text);
			}

			tone_analyzer.tone({ text: unescape(tweets.join(" ")) }, function(err, tone){
				if (err) 
					return response.json('Error processing the request');		
				else {
					var results = [];
					var playlists = [];
					var pe = util.getPersonalityEmotion(tone);
					var promise = Playlist.find({'emotion': emotion}).exec();

					promise.then(function(playlist){
						playlists.push(playlist);
					});

					Promise.all(promise).then(function(){
						playlists = playlists[0]
						for(var i = 0; i < playlists.length; i++){
							var similarity = util.similarity(pe.personality, playlists[i].personality.split(','));
							console.log("similarity", similarity);
							if (similarity > pi_threshold){
								results.push(playlists[i])
							}
						}
						return response.json(results);
					});	
				}
			});
		});
	}
});

router.post('/api/personality/analyze', function(request, response, next){
	if (typeof request.body.text !== 'undefined'){
		var text = request.body.text;

		var payload = {
			text: unescape(request.body.text)
		};
		tone_analyzer.tone(payload, function(err, tone){
			if (!err) { 
				var personality = util.getPersonalityEmotion(tone);
				return response.json(personality);
			}
			else {
				return response.json('Error processing the request');		
			}
		});
	}
	else{
		return response.json("Invalid request");
	}	
});



router.post('/api/emotion/load', function(request, response, next){
	if (typeof request.body.lyrics !== 'undefined' && 
		typeof request.body.emotion !== 'undefined' &&
		typeof request.body.artist !== 'undefined' &&
		typeof request.body.name !== 'undefined'){

		var lyrics = request.body.lyrics;
		var emotion = request.body.emotion;
		var artist = request.body.artist;
		var name = request.body.name;

		var track 		= new Track();
		track.artist 	= artist;
		track.name 		= name;
		track.lyrics 	= lyrics;
		track.emotion 	= emotion;

		track.save(function(err){
			if(err)
				response.json({ error: err });
			else {
				response.json({			
					output: classifier.learn(lyrics, emotion),
					song: name,
					artist: artist,
					emotion: emotion
				});
			}			
		});
	}
	else response.json("Invalid request");
});



router.post('/api/emotion/track', function(request, response, next){
	if (typeof request.body.lyrics !== 'undefined'){
		var lyrics = request.body.lyrics;
		response.json({			
			emotion: classifier.categorize(lyrics)
		});
	}
	else{
		response.json("Invalid request");
	}	
});




router.post('/api/playlist', function(request, response, next){
	if (typeof request.body.id !== 'undefined' && 
		typeof request.body.name !== 'undefined' &&
		typeof request.body.user_id !== 'undefined' &&
		typeof request.body.personality !== 'undefined' &&
		typeof request.body.emotion !== 'undefined' &&
		typeof request.body.image !== 'undefined'){

		var id 			= request.body.id;
		var name 		= request.body.name;
		var user_id 	= request.body.user_id;
		var personality = request.body.personality;
		var emotion 	= request.body.emotion;
		var image 		= request.body.image;

		var playlist = new Playlist({ _id: id});		
		playlist.name 			= name;
		playlist.user_id 		= user_id;
		playlist.personality 	= personality;
		playlist.emotion 		= emotion;
		playlist.image 			= image;


		Playlist.count({_id: id}, function (err, count) {
			if (!count) {
				playlist.save(function(err){
					if(err)
						response.json({ error: err });
					else {
						response.json({			
							output: "Playlist created!",
							personality: personality,
							name: name,
							emotion: emotion
						});
					}			
				});
			}
			else response.json({ output: "Playlist alreadt exists"});
		});
	}
	else response.json("Invalid request");
});



router.post('/api/track', function(request, response, next){
	var track = new Track();
	track.artist 	= request.body.artist;
	track.name 		= request.body.name;
	track.lyrics 	= request.body.lyrics;
	track.emotion 	= request.body.emotion;

	track.save(function(err){
		if(err)
			response.send(err);
		response.json("Track created!");
	});
});





module.exports = router;

function apiError(res) {
	return function (error) {
		if (!isApiError(error)) logger.error(error);

		var reportedError = getReportedError(error);
		res.status(reportedError.code).json(reportedError);
	};
}