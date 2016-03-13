var fs      = require("fs");
var bayes   = require("bayes"); 
var request = require("request");
var cheerio = require("cheerio");
var querystring = require('querystring');
var slashes = require('slashes');
var Promise         = require('bluebird');
var mongoose        = Promise.promisifyAll(require('mongoose'));

var Track        = require('./../models/track');

var classifier  = bayes();


module.exports.load_training = function(){
    var tracks = [];
    var promise = Track.find().exec();

    promise.then(function(track){
        tracks.push(track);
    });

    Promise.all(promise).then(function(){
        tracks = tracks[0]
        for(var i = 0; i < tracks.length; i++){
            classifier.learn(tracks[i].lyrics, tracks[i].emotion);
        }
    }); 

    /*
    var baseUrl = "http://api.musixmatch.com/ws/1.1/matcher.track.get?";
    var stream  = fs.readFileSync("./data/training_data.json");
    var data = JSON.parse(stream);

    for (var i = 0; i < data.length ; i++){
        var track = data[i].song;
        var artist = data[i].artist;
        var emotion = data[i].emotion;
        var payload = {
            "apikey": "0bcd220b9ee2b77e21cf75a8456dc98a",
            "f_has_lyrics": 1,
            "q_track": track,
            "q_artist": artist,
            "format": "json",
        };

        var url = baseUrl + querystring.stringify(payload);

        request({ url: url, rejectUnauthorized: false }, function(error, response, result){
            try {
                if(!error) {
                    var stripped = JSON.parse(slashes.strip(result));
                    var track_list = stripped.message.body;

                    if(track_list && typeof track_list.track !== 'undefined'){                        
                        var lyrics_url = track_list.track.track_share_url;

                        request(lyrics_url, function(l_error, l_response, l_result){
                            try {
                                if(!l_error){
                                    var $ = cheerio.load(l_result);
                                    var lyrics = $('#selectable-lyrics div span').text();

                                    if(lyrics.length > 0){
                                        classifier.learn(lyrics, emotion);
                                        console(emotion);
                                    }
                                }
                                else {
                                    console.log("Error scrapping", l_error);
                                }
                            } catch(e){ console.log("Error scrapping", e); }
                        });   

                    }
                }
                else {
                    console.log("Error API", error);
                }
            } catch(e){ console.log("Error API", e, url); }
        });
    }
    */
};




module.exports.learn = function(lyrics, emotion){
    try {
        classifier.learn(lyrics, emotion);
        return "Learning successful";
    } catch(e){ return "Error: cannot learn"; }
};

module.exports.categorize = function(text){
    return classifier.categorize(text);
};