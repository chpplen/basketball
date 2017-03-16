# encoding: utf-8

import csv
import requests 
from bs4 import BeautifulSoup 
import HTMLParser 

from datetime import date
from datetime import timedelta

def crawler():
	url = 'https://www.playsport.cc/livescore.php?aid=3&gamedate=%s&mode=11'

	teamMap = {u"公牛":0,u"溜馬":1,u"籃網":2,u"巫師":3,u"熱火":4,u"塞爾提":5,u"尼克":6,u"鵜鶘":7,u"公鹿":8,u"灰狼":9
			  ,u"快艇":10,u"火箭":11,u"活塞":12,u"老鷹":13,u"拓荒者":14,u"馬刺":15,u"76人":16,u"金塊":17,u"小牛":18,u"勇士":19
			  ,u"灰熊":20,u"國王":21,u"魔術":22,u"騎士":23,u"黃蜂":24,u"太陽":25,u"爵士":26,u"雷霆":27,u"暴龍":28,u"湖人":29}

	links = []
	dateList = []

	today = date.today()

	t = date(2016, 10, 26)
	while today >= t:
		dateList.append(t.strftime("%Y%m%d"))
		links.append(url%t.strftime("%Y%m%d"))
		t += timedelta(1)

	# print links

	with open('data/basketballRecord.csv', 'wb') as csvfile:
		spamwriter = csv.writer(csvfile)

		for i in range(len(links)):			
			# print links[i]
			print dateList[i] + " processing..."

			res = requests.get(links[i]) 
			soup = BeautifulSoup(res.text.encode("utf-8"), "html.parser")  
			
			shop_table = soup.findAll('table', {"class":"scorebox"})
			

			for table in shop_table:
				# print table
				status = table.findAll('tr')
				index = 0
				for s in status: 
					index += 1
					if index == 1:
						continue

					# print s.find('th').string
					record = []
					# print teamMap[s.find('th').string]
					record.append(teamMap[s.find('th').string])

					record.append(dateList[i])

					td_shop = s.findAll('td')
					for score in td_shop:
						record.append(score.string)
						# print v.string
					spamwriter.writerow(record)
