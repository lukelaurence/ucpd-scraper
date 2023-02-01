import requests,time,datetime,re
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim

def scrapeucpd(new=True):
	param='x' if new else 'r+'
	with open("reports.txt",param) as f:
		if new:
			startdate="1277960400"
		else:
			for x in f:
				pass
			xy=re.split(' |/|:',x.split('\t',3)[2])
			p=[int(y) for y in xy[:-1]]
			if xy[-1]=='PM':
				p[3]+=12
			year=p.pop(2)+2000
			p=[year]+p
			d=datetime.datetime(*p,tzinfo=datetime.timezone.utc)
			dtstart=datetime.datetime(year,3,1,1,tzinfo=datetime.timezone.utc)
			dtstart+=datetime.timedelta(13-datetime.date.weekday(dtstart))
			dtend=datetime.datetime(year,11,1,tzinfo=datetime.timezone.utc)
			dtend+=datetime.timedelta(6-datetime.date.weekday(dtend))
			tz=5 if dtstart<d<dtend else 6
			d+=datetime.timedelta(hours=tz)
			startdate=str(int(datetime.datetime.timestamp(d)))
		enddate=str(int(time.time()))
		baseurl=f"https://incidentreports.uchicago.edu/incidentReportArchive.php?startDate={startdate}&endDate={enddate}&offset="
		response=requests.get(baseurl+'0')
		soup=BeautifulSoup(response.text,"html.parser")
		pages=int(soup.find('span',class_='page-link').text[4:])*5
		for page in range(0,pages,5):
			response=requests.get(baseurl+str(page))
			soup=BeautifulSoup(response.text,"html.parser")
			rows = soup.find('tbody').findAll('tr')
			for r in rows:
				if len(r)==15:
					cells=r.findAll('td')
					i = [c.text.replace('\n',' ') for c in cells]
					if '' not in i and 'Void' not in i and 'VOID' not in i:
						f.write("\t".join(i)+'\n')
			time.sleep(1)

def geotag():
	gl = Nominatim(user_agent="example app")
	addresses = set()
	with open("reports.txt",'r') as f:
		for x in f:
			a = x.split('\t')[1]
			if '(' in a:
				a = a.split('(',1)[0]
			addresses.add(a.strip())
	with open("address_coords.txt",'r+') as f2:
		seen = [u.split('\t')[0] for u in f2]
		for y in addresses:
			if y not in seen:
				q = {'city':'Chicago','county':'Cook','state':'IL'}
				q['street'] = y
				addr = gl.geocode(query=q)
				if addr != None:
					f2.write('\t'.join([y,str(addr.latitude),str(addr.longitude)+'\n']))
				else:
					f2.write('\t'.join([y,"Address not found\n"]))
				seen.append(y)
				time.sleep(5)
