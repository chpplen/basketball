from crawler import crawler
from featuresExtraction import featuresExtraction
from train import train
from predict import predict
import pickle

def main():
	crawler()

	FE = featuresExtraction()
	FE.extraction()

	t = train()
	t.trainModel()

	predict()


if __name__ == "__main__":
	main()