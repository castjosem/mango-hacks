var express 		= require('express');
var mongoose 		= require('mongoose');
var fs 				= require('fs');
var path 			= require('path');
var favicon 		= require('serve-favicon');
var logger 			= require('morgan');
var cookieParser 	= require('cookie-parser');
var bodyParser 		= require('body-parser');
var config        	= require('./config/config');
var config        	= require('./config/config');
var playlist 		= require('./routes/playlist');
var model_playlist = require('./models/playlist');
var routes 			= require('./routes/index');

var classifier 		= require('./modules/classifier');

var app 			= express();

var connect = function () {
	console.log('connect-to-mongodb');
	var options = {
		server: 	{ socketOptions: { keepAlive: 1, connectTimeoutMS: 30000 } },
		replset: 	{ socketOptions: { keepAlive: 1, connectTimeoutMS : 30000 } }
	};
	mongoose.connect(config.mongodb, options);
};
connect();

mongoose.connection.on('error', console.log.bind(console, 	'mongoose-connection-error:'));
mongoose.connection.on('open', 	console.log.bind(console,'	connect-to-mongodb'));
mongoose.connection.on('disconnected', connect);


// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

// uncomment after placing your favicon in /public
//app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')));
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));


app.use('/', routes);
app.use('/', playlist);

classifier.load_training();

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  var err = new Error('Not Found');
  err.status = 404;
  next(err);
});

module.exports = app;
