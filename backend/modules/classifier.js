var csv 	= require("fast-csv");
var fs 		= require("fs");
var stream 	= fs.createReadStream("./data/training_data.csv");
var bayes 	= require("bayes");	
var request = require("request");
var cheerio = require("cheerio");


var classifier	= bayes();


module.exports.load_training = function(){
	var baseUrl = "https://www.musixmatch.com/ws/1.1/macro.search";
	var headers = {
    	'Content-Type': 'text/html'
	};
	var payload = {
		url: baseUrl,
		method: "GET",
		headers: headers,
		qs: {
			"app_id": "community-app-v1.0", 
			"guid": "b1f6f4c4-3995-4a01-925d-badc2d02d3de",
			"format": "json",
			"page_size": "1",
			"part": "artist_image",
			"q": ""
		}
	};

	var csvStream = csv()
	    .on("data", function(data){
	    	var row = data;

	    	var track = row[0];
	    	var artist = row[1];
	    	var emotion = row[2];

	    	payload.qs.q = track + " " + artist;

         	function callback (error, response, body) {
			    if (!error && response.statusCode == 200) {			    	
			    	var lyrics = JSON.parse(body);
			    	lyrics_url = String(lyrics.message.body.macro_result_list.track_list[0]);
			    	if (typeof lyrics_url !== 'undefined' && lyrics_url){
			    	}
			    }
			};

			request(payload, callback);

	    })
	    .on("end", function(){   });

	stream.pipe(csvStream);

};

