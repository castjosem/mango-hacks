<h1><p align="center"><a href="http://devpost.com/software/moodsical" target="_blank">Moodsical</a></p></h1>

<p align="center">
  <a href="http://mangohacks16.devpost.com/"><b>MangoHacks 2016</b></a>
</p>

<p align="center">
<br>
|
<b><a href="#inspiration"> Inspiration </a></b>|
<b><a href="#what-it-does"> What it does </a></b>|
<b><a href="#how-we-built-it"> How its built </a></b>

</p>

---

## Inspiration
We love listening to music! But what if we could listen things that are alike us and of how we feel!
Going through spotify looking for interesting playlists can be little boring! Specially if we are not in the mood for it!
We got inspired by the fact of being able to find the playlist we are looking for :)!

## What it does
Moodsical is a machine learning app that understands emotions within music and shares that to you!
It requests for your twitter username in order to study your latest tweets and understand your personality.
By knowing you a little bit more it is able to deliver you playlists according to this.
But!, moodsical will ask you for your current mood and with this will suggest you playlists that matches your personality and mood selected!

## How we built it
Moodsical uses Watson's Tone Analyzer to learn from your latest tweets and create a vector that represents you based on: Openess, Conscientiousness
, Extraversion, Agreeableness, Emotional Range

Using a Naive Bayes Classifier we are able to categorize song emotions based on its lyrics. We created our training data using Spotify's Data Miner tool to roughly gather 100 songs per emotion (happy, sad, angry, relaxing, excited). With this our API can classify any song's lyric and give back its emotion.

By having this classifier we are able to as well categorize the main emotion of a playlist and create a "personality" for it that it's matched with you thorugh a mathematical formula.

To load data into the classifier we built python scripts that read from our training data and loads it into a MongoDB database and searches for featured playlists from Spotify to increase our dataset.

Currently running on a DigitalOcean server:  45.55.105.121:3000
Emotions:  Happy, Sad, Angry, Relaxing, Excited

Important Endpoints:
	GET /api/playlist/search?emotion=Happy&username=Pharrell     Get playlists 

	POST /api/personality/analyze    text = ?		Analyze text and calculate its "personality"

	POST /api/emotion/track    lyrics = ?     Analyze lyric and calculate its emotion


## Challenges we ran into
Watson Tone Analyzer permits to identify emotions from Text. Although for music is not a good classifier. A lot of time was spent looking for ways to identify an appropiate solution to get the emotions.
In order to get songs lyrics, there are no API that gives access to the complete lyric. In this light, we had to use Musicxmatch API to search for the url of the web version of the lyric and use Web Scrapping tools to obtain it.

## Accomplishments that we're proud of
We are able to give a reasonable classification for song emotions to identify the playlist we are looking for!
It's amazing to use machine learning to solve problems!

## What we learned
Machine Learning is beautiful. 

## What's next for Moodsical
Increase dataset size to provide better and better suggestions! 
Make people happier! :)


## Important links
Spotify Playlist Miner  http://static.echonest.com/playlistminer/index.html
