from dataload import *
import os

class TrainClassifier(object):
	def __init__(self):
		self.classifier = Classifier()

	def train(self, file_path = None):
		return self.classifier.train(file_path)

if __name__ == "__main__":
	print ("Start train_classifier.py")

	file_name =  "training_data.json"
	script_dir = os.path.dirname(__file__)
	file_path = os.path.join( script_dir, '..', 'data', file_name)

	train_classifier = TrainClassifier()
	train_classifier.train(file_path)

	print ("End train_classifier.py")
