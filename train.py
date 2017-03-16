from sklearn.ensemble import RandomForestClassifier
from bayes_opt import BayesianOptimization
from sklearn.model_selection import cross_val_score
from sklearn.externals import joblib
import csv

class train:
	def __init__(self):

		self.train_X = []
		self.train_Y = []

		self.test_X = []
		self.test_Y = []

		spamreader = csv.reader(open('data/basketballFeatures.csv', 'rb'))

		index = 0
		for row in spamreader:
			index += 1
			if index < 200:
				continue

			if index < 400:
				self.train_Y.append(row[0])
				temp = []
				for i in range(1,len(row)):
					temp.append(row[i])
				self.train_X.append(temp)
			else:
				self.test_Y.append(row[0])
				temp = []
				for i in range(1,len(row)):
					temp.append(row[i])
				self.test_X.append(temp)

		print "train size: " + str(len(self.train_Y))
		print "test size: " + str(len(self.test_Y))

	def rfrcv(self, n_estimators, min_samples_split, max_features, max_depth, min_impurity_split, min_weight_fraction_leaf):
	    return cross_val_score(RandomForestClassifier(n_estimators=int(n_estimators),
	                               min_samples_split=int(min_samples_split),
	                               max_features=min(max_features, 0.999),
	                               max_depth=int(max_depth),
	                               min_impurity_split=min_impurity_split,
	                               min_weight_fraction_leaf=min_weight_fraction_leaf,
	                               random_state=2),
	                           self.train_X, self.train_Y, cv=5).mean()

	def getConfusionMatrics(self, labelReal, labelPro, thres):
		TN = 0
		FP = 0
		FN = 0
		TP = 0
		for i in range(len(labelReal)):
			predict = 0
			if labelPro[i][1] > thres:
				predict = 1

			if int(labelReal[i]) == 0 and predict == 0:
				TN += 1
			elif int(labelReal[i]) == 0 and predict == 1:
				FP += 1
			elif int(labelReal[i]) == 1 and predict == 0:
				FN += 1
			else:
				TP += 1	
		recall = TP/(TP + FN + 0.0)
		precision = TP/(TP + FP + 0.0)
		accuracy = (TP+TN)/(TN+FP+FN+TP+0.0)
		return [thres,TN,FP,FN,TP,recall,precision,accuracy]


	def trainModel(self):
		rfcBO = BayesianOptimization(self.rfrcv, {'n_estimators': (10, 250),
											'min_samples_split': (2, 25),
											'max_features': (0.1, 0.999),
											'max_depth': (1, 20),
											'min_impurity_split':(1e-8,1e-6),
											'min_weight_fraction_leaf':(0,0.1)})
		rfcBO.maximize()

		print '-'*53
		print 'Final Results' 
		print rfcBO.res['max']
		# print rfcBO.res['max']['max_val']
		print rfcBO.res['all']

		paramsAll = rfcBO.res['all']['params']
		valuesAll = rfcBO.res['all']['values']

		estimator = None
		with open('data/rfc_record.csv', 'wb') as csvfile:
			spamwriter = csv.writer(csvfile)
			spamwriter.writerow(["score","n_estimators","min_samples_split","max_features","max_depth","min_impurity_split","min_weight_fraction_leaf"])
			for i in range(len(valuesAll)):
				temp = []
				temp.append(valuesAll[i])
				temp.append(paramsAll[i]['n_estimators'])
				temp.append(paramsAll[i]['min_samples_split'])
				temp.append(paramsAll[i]['max_features'])
				temp.append(paramsAll[i]['max_depth'])
				temp.append(paramsAll[i]['min_impurity_split'])
				temp.append(paramsAll[i]['min_weight_fraction_leaf'])
				spamwriter.writerow(temp)

			params = rfcBO.res['max']['max_params']

			estimator = RandomForestClassifier(n_estimators=int(params['n_estimators'])
											,min_samples_split=int(params['min_samples_split'])
											,max_features=min(params['max_features'], 0.999)
											,max_depth=int(params['max_depth'])
											,min_impurity_split=params['min_impurity_split']
											,min_weight_fraction_leaf=params['min_weight_fraction_leaf'])
			estimator.fit(self.train_X, self.train_Y)
			test_score = estimator.score(self.test_X, self.test_Y)
			print('Test accuracy score: %.4f' % test_score)

			spamwriter.writerow(["train_score",rfcBO.res['max']['max_val'],"test_score",test_score])

			with open('data/rfc_best.csv', 'wb') as csvfileBest:
				spamwriterBest = csv.writer(csvfileBest)
				temp = []
				temp.append(params['n_estimators'])
				temp.append(params['min_samples_split'])
				temp.append(params['max_features'])
				temp.append(params['max_depth'])
				temp.append(params['min_impurity_split'])
				temp.append(params['min_weight_fraction_leaf'])
				spamwriterBest.writerow(temp)


		with open('data/predict.csv', 'wb') as csvfile:
			spamwriter = csv.writer(csvfile)

			pro = estimator.predict_proba(self.test_X)
			pre = estimator.predict(self.test_X)

			spamwriter.writerow(["thres","TN","FP","FN","TP","recall","precision","accuracy"])
			for i in xrange(20):
				temp = self.getConfusionMatrics(self.test_Y,pro,0.5+i*0.01)
				spamwriter.writerow(temp)

		joblib.dump(estimator, 'model/model.pkl') 


