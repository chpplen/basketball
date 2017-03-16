# encoding: utf-8
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
import csv
import pickle
from datetime import date, timedelta
import requests 
from bs4 import BeautifulSoup 
import HTMLParser 


def load(thres):
	train_X = []
	train_Y = []
	index = 0

	spamreader = csv.reader(open('data/basketballFeatures.csv', 'rb'))
	for row in spamreader:
		index += 1
		if index < thres:
			continue
		else:
			train_Y.append(row[0])
			temp = []
			for i in range(1,len(row)):
				temp.append(row[i])
			train_X.append(temp)

	print "train size: " + str(len(train_Y))
	return train_X, train_Y

def scoreFrom70(team1Get,team2Lost):
	if team1Get > team2Lost:
		return (team1Get*2 + team2Lost)/3.0
	elif (team1Get + 10) > team2Lost:
		return team1Get
	else:
		return (team1Get + team2Lost)/2.0

def getNewX(X):
	newX = []
	for x in X:
		x.append(scoreFrom70(x[0],x[4]))
		x.append(scoreFrom70(x[3],x[1]))
		newX.append(x)
	return newX


def featuresGenerate(team1, team2, FE, today):
	x = []


	historyTeam1 = FE.historyAverage[team1]
	x.append(historyTeam1["aveGet"])
	x.append(historyTeam1["aveLost"])
	# x.append(scoreTeam1)
	if FE.isLastdayFight(today,team1):
		x.append(1)
	else:
		x.append(0)


	historyTeam2 = FE.historyAverage[team2]
	x.append(historyTeam2["aveGet"])
	x.append(historyTeam2["aveLost"])
	# x.append(scoreTeam2)
	if FE.isLastdayFight(today,team2):
		x.append(1)
	else:
		x.append(0)

	x.append(FE.scoreFrom70(historyTeam1["aveGet"],historyTeam2["aveLost"]))
	x.append(FE.scoreFrom70(historyTeam2["aveGet"],historyTeam1["aveLost"]))

	return x


def predict():
	FE = pickle.load(open('model/featuresExtraction.pkl', 'rb'))

	# estimator = joblib.load('model/model.pkl') 

	spamreader = csv.reader(open('data/rfc_best.csv', 'rb'))
	for params in spamreader:
		estimator = RandomForestClassifier(n_estimators=int(float(params[0]))
											,min_samples_split=int(float(params[1]))
											,max_features=min(float(params[2]), 0.999)
											,max_depth=int(float(params[3]))
											,min_impurity_split=float(params[4])
											,min_weight_fraction_leaf=float(params[5]))

	# estimator = RandomForestClassifier(n_estimators=159
	# 									,min_samples_split=2
	# 									,max_features=0.9717
	# 									,max_depth=2
	# 									,min_impurity_split=7.5337e-07
	# 									,min_weight_fraction_leaf=0.057)

	today = (date.today()).strftime("%Y%m%d")
	tomorrow = (date.today()+timedelta(1)).strftime("%Y%m%d")
	print "today: " + today
	print "tomorrow: " + tomorrow

	url = 'https://www.playsport.cc/livescore.php?aid=3&gamedate=%s&mode=11'%tomorrow
	teamMap = {u"公牛":"0",u"溜馬":"1",u"籃網":"2",u"巫師":"3",u"熱火":"4",u"塞爾提":"5",u"尼克":"6",u"鵜鶘":"7",u"公鹿":"8",u"灰狼":"9"
			  ,u"快艇":"10",u"火箭":"11",u"活塞":"12",u"老鷹":"13",u"拓荒者":"14",u"馬刺":"15",u"76人":"16",u"金塊":"17",u"小牛":"18",u"勇士":"19"
			  ,u"灰熊":"20",u"國王":"21",u"魔術":"22",u"騎士":"23",u"黃蜂":"24",u"太陽":"25",u"爵士":"26",u"雷霆":"27",u"暴龍":"28",u"湖人":"29"}

	res = requests.get(url) 
	soup = BeautifulSoup(res.text.encode("utf-8"), "html.parser")  
	shop_table = soup.findAll('table', {"class":"no_start_team"})

	teamList = []
	for table in shop_table:
		team1 = table.find('td', {"class":"team_left"}).string
		team2 = table.find('td', {"class":"team_right"}).string
		x = [teamMap[team1], teamMap[team2]]
		teamList.append(x) 

	X = []
	for team in teamList:
		X.append(featuresGenerate(team[0],team[1],FE,tomorrow))
	print X

	with open('predict/predict_'+tomorrow+'.csv', 'wb') as csvfile:
		spamwriter = csv.writer(csvfile)
		spamwriter.writerow(["Data number", "Team1", "Team2", "Probability", "Predict"])
			
		for number in xrange(200,500,50):
			train_X, train_Y = load(number)
			
			estimator.fit(train_X, train_Y)

			proba = estimator.predict_proba(X)
			pre = estimator.predict(X)
			print proba
			print pre

			for i in range(len(teamList)):
				spamwriter.writerow([len(train_X),teamMap.keys()[teamMap.values().index(teamList[i][0])].encode('big5'),teamMap.keys()[teamMap.values().index(teamList[i][1])].encode('big5'),proba[i],pre[i]])

# predict()