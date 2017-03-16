# encoding: utf-8

import datetime
import csv
import pickle

class featuresExtraction:
	def __init__(self):
		self.dayLastFight = {}
		self.historyAverage = {}

		t = datetime.date(2016, 10, 24)
		for i in range(30):
			self.historyAverage.update({str(i):{"aveGet":0.0,"aveLost":0.0,"count":0}})
			self.dayLastFight.update({str(i):t})

	def updateAve(self, scoreGet, scoreLost, teamDict):
		aveGet = teamDict["aveGet"]
		aveLost = teamDict["aveLost"]
		count = teamDict["count"]
		totalGet = aveGet*count + scoreGet
		totalLost = aveLost*count + scoreLost

		count += 1
		teamDict["count"] = count
		teamDict["aveGet"] = totalGet/count
		teamDict["aveLost"] = totalLost/count

		return teamDict

	def isLastdayFight(self, d, team):
		today = datetime.datetime.strptime(d, "%Y%m%d").date()
		lastFight = self.dayLastFight[team]
		diff = (today - lastFight).days
		self.dayLastFight[team] = today
		if diff == 1:
			return True
		else:
			return False

	def scoreFrom70(self, team1Get,team2Lost):
		if team1Get > team2Lost:
			return (team1Get*2 + team2Lost)/3.0
		elif (team1Get + 10) > team2Lost:
			return team1Get
		else:
			return (team1Get + team2Lost)/2.0



	def featuresGenerate(self, team1, team2):
		x = []

		# print team1
		team1Index = team1[0]
		scoreTeam1 = int(team1[2])

		historyTeam1 = self.historyAverage[team1Index]
		x.append(historyTeam1["aveGet"])
		x.append(historyTeam1["aveLost"])
		# x.append(scoreTeam1)
		if self.isLastdayFight(team1[1],team1Index):
			x.append(1)
		else:
			x.append(0)


		team2Index = team2[0]
		scoreTeam2 = int(team2[2])

		historyTeam2 = self.historyAverage[team2Index]
		x.append(historyTeam2["aveGet"])
		x.append(historyTeam2["aveLost"])
		# x.append(scoreTeam2)
		if self.isLastdayFight(team2[1],team2Index):
			x.append(1)
		else:
			x.append(0)

		x.append(self.scoreFrom70(historyTeam1["aveGet"],historyTeam2["aveLost"]))
		x.append(self.scoreFrom70(historyTeam2["aveGet"],historyTeam1["aveLost"]))

		self.updateAve(scoreTeam1,scoreTeam2,self.historyAverage[team1Index])
		self.updateAve(scoreTeam2,scoreTeam1,self.historyAverage[team2Index])

		y = 1
		if scoreTeam1 > scoreTeam2:
			y = 0
		return x, y

	def extraction(self):

		X = []
		Y = []

		spamreader = csv.reader(open('data/basketballRecord.csv', 'rb'))

		index = 0
		temp = []
		for row in spamreader:
			index += 1
			if index%2 == 1:
				temp = row
			else:
				try:
					x, y = self.featuresGenerate(temp,row)
					X.append(x)
					Y.append(y)
				except Exception:
					print Exception

		spamwriter = csv.writer(open('data/basketballFeatures.csv', 'wb'))
		for i in range(len(Y)):
			temp = [Y[i]]
			spamwriter.writerow(temp+X[i])

		pickle.dump(self, open('model/featuresExtraction.pkl', 'wb'))
