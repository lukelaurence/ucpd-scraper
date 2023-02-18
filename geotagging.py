import time
from geopy.geocoders import Nominatim

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
				f2.write('\t'.join([y,"Address not found\n"]))
				q = {'city':'Chicago','county':'Cook','state':'IL'}
				q['street'] = y
				addr = gl.geocode(query=q)
				if addr != None:
					f2.write('\t'.join([y,str(addr.latitude),str(addr.longitude)+'\n']))
				else:
					f2.write('\t'.join([y,"Address not found\n"]))
				seen.append(y)
				time.sleep(5)

def issingleaddress(input):
	stopterms = [' and ','&',' to ',' between ',' near ',' at ']
	for x in stopterms:
		if x in input:
			return False
	return True

def fixgaps():
	with open("address_coords.txt",'r') as f:
		addresses = {}
		notfound = set()
		for x in f:
			a,*b = x.split('\t')
			if len(b) == 2:
				addresses[a] = b
			else:
				notfound.add(a)
		for y in notfound:
			for z in addresses.keys():
				if ' '+z in ' '+y and issingleaddress(y):
					addresses[y] = addresses[z]
					break
		with open("address_coords_revised.txt",'w') as f2:
			for k,[v1,v2] in addresses.items():
				f2.write('\t'.join([k,v1,v2]))