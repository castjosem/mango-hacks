var express 		= require('express');
var	config  		= require('./../config/config');
var util 			= require('./../util/utilities');
var Playlist 		= require('./../models/playlist');
var router 			= express.Router();
var Promise 		= require('bluebird');
var mongoose 		= Promise.promisifyAll(require('mongoose'));
var watson 			= require('watson-developer-cloud');
var tone_analyzer 	= new watson.tone_analyzer(config.services.tone_analyzer);
var twitter_config 	= config.api.twitter;
var Twit 			= Promise.promisifyAll(require('twit'));
var pi_threshold 	= config.pi_threshold;


router.get('/', function(req, res, next) {
	res.render('index', { title: 'Express' });
});



router.post('/api/search', function(request, response, next){
	if (typeof request.body.username !== 'undefined' && typeof request.body.emotion !== 'undefined'){
		var username = request.body.username;
		var T = new Twit({
			consumer_key:         twitter_config.consumer_key,
			consumer_secret:      twitter_config.consumer_secret,
			access_token:         twitter_config.access_token,
			access_token_secret:  twitter_config.access_token_secret,
			timeout_ms:           60*1000
		});
		var options = { screen_name: username,  count: twitter_config.count };
		var tweets = [];

		T.get('statuses/user_timeline', options , function(err, data) {

			for (var i = 0; i < data.length ; i++) {
				tweets.push(data[i].text);
			}
					
			var emotion = request.body.emotion;
			var text = request.body.text;

			console.log(tweets.join(" "));

			var payload = {
				text: unescape(tweets.join(" "))
			};

			tone_analyzer.tone(payload, function(err, tone){
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



router.post('/api/analyze', function(request, response, next){
	if (typeof request.body.text !== 'undefined'){
		//console.log(request.body.text);

		var payload = {
			text: unescape(request.body.text)
		};
		tone_analyzer.tone(payload, function(err, tone){
			if (err) 
				return response.json('Error processing the request');		
			else {
				var personality = util.getPersonalityEmotion(tone);
				return response.json(personality);
			}
		});
	}
	else{
		request.json("Invalid request");
	}	
});



module.exports = router;

function apiError(res) {
	return function (error) {
		if (!isApiError(error)) logger.error(error);

		var reportedError = getReportedError(error);
		res.status(reportedError.code).json(reportedError);
	};
}