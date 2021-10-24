# scraping imports
import requests
import urllib.request
import time
import re
from bs4 import BeautifulSoup
# plotting imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# geolocating imports
from geopy.geocoders import Nominatim
gl = Nominatim(user_agent="example app")

def scrapeucpd():
	lst = [[],[],[],[],[],[],[]]
	addresses = {}
	enddate = str(int(time.time()))
	baseurl = "https://incidentreports.uchicago.edu/incidentReportArchive.php?startDate=1277960400&endDate=" + enddate + "&offset="
	url = baseurl + '0'
	response = requests.get(url)
	soup = BeautifulSoup(response.text,"html.parser")
	pages = int(soup.findAll('span')[-3].text[4:]) * 5
	# pages = 5
	for p in range(0,pages,5):
		offset = str(p)
		url = baseurl + offset
		response = requests.get(url)
		soup = BeautifulSoup(response.text,"html.parser")
		tags = soup.findAll('td')
		for x,y in enumerate(tags):
			a = x % 7
			y = y.text
			if not a - 1:
				y = re.sub(r"\([^()]*\)","",y) + ", Chicago, IL"
				if y in addresses:
					y = addresses.get(y)
				else:
					adrs = gl.geocode(y)
					# if adrs == None:
					# 	print(y)
					addresses[y] = adrs
					y = adrs
			lst[a].append(y)
		# time.sleep(1)
	return(lst)

def getxandy(input):
	x,y = ([],[])
	for b in input:
		if b == None:
			x.append(0)
			y.append(0)
		else:
			x.append(b[1][0])
			y.append(b[1][1])
	return (np.array(x),np.array(y))

def getlocations(input):
	output = []
	for x in input:
		if x == None:
			output.append("Geolocation Failed")
		else:
			output.append(x[0])
		return(np.array(output))

df = scrapeucpd()
x,y = getxandy(df[1])
s = 0.5
c = '#800000'
# background = plt.imread('4.png')
# incidents = np.array(df[0])
# locations = getlocations(df[1])
occurred = np.array(df[3])
comments = np.array(df[4])
bounds = (41.7,41.9,-87.7,-87.5)
fig, ax = plt.subplots()
ax.set_title("Visualize a map of Hyde Park here")
ax.set_xlim(bounds[0],bounds[1])
ax.set_ylim(bounds[2],bounds[3])
sc = plt.scatter(x,y,s=s,c=c)

annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
					bbox=dict(boxstyle="round", fc="w"),
					arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

def update_annot(ind):
	pos = sc.get_offsets()[ind["ind"][0]] 
	annot.xy = pos
	n = ind["ind"][0]
	text = "{}\n{}".format(comments[n],occurred[n])
	# text = "{}\n{}".format(" ".join([incidents[n] for n in ind["ind"]]), 
	# 					#    " ".join([locations[n] for n in ind["ind"]]),
	# 					#    " ".join([occurred[n] for n in ind["ind"]]),
	# 					   " ".join([comments[n] for n in ind["ind"]]))
	annot.set_text(text)
	annot.get_bbox_patch().set_facecolor('#800000')
	annot.get_bbox_patch().set_alpha(0.4)

def hover(event):
	vis = annot.get_visible()
	if event.inaxes == ax:
		cont,ind = sc.contains(event)
		if cont:
			update_annot(ind)
			annot.set_visible(True)
			fig.canvas.draw_idle()
		else:
			if vis:
				annot.set_visible(False)
				fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", hover)

# plt.imshow(background)
plt.show()
# x = np.array(df[1][0])
# y = np.array(df[1][1])
# incident = np.array(df[0])
# location = np.array(df[1])