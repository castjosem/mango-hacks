

module.exports.getPersonalityEmotion = function(tone){
	var emotion_tone = tone.document_tone.tone_categories[0].tones;
	var writting_tone = tone.document_tone.tone_categories[1].tones;
	var social_tone = tone.document_tone.tone_categories[2].tones;

	var emotion_index = 0;
	for(var i = 1 ; i < emotion_tone.length; i++){
		if(emotion_tone[i].score > emotion_tone[emotion_index].score)
			emotion_index = i;
	}

	var emotion_relevant = emotion_tone[emotion_index];
	var personality = [];
	for(var i = 0 ; i < social_tone.length; i++){
		personality.push(social_tone[i].score);
	}

	return {
		emotion: emotion_relevant, 
		personality: personality
	};
};



module.exports.similarity = function(A, B){
	if (typeof A === 'undefined ' || typeof B === 'undefined' || A.length != B.length) return 0;
	var distance = 0.0;	
	var n = A.length;
	for(var i = 0 ; i < n ; i++) {
		distance += Math.pow(A[i] - B[i], 2);
	}
	return 1 - (Math.sqrt(distance / n));
};