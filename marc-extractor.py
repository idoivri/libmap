from bs4 import BeautifulSoup
import json
import requests

soup = BeautifulSoup(open("marcxml.xml"),"xml")

f = open('librarylocations.json','w')

#get JSON dict containing the geometry for the 
def get_geocode(address):
   
   url = 'http://maps.googleapis.com/maps/api/geocode/json'
   res = requests.get(url, params={
            'address': address,
            'sensor': 'false'
    	})

   json_obj = json.loads(res.content)

   result = json_obj['results'][0]
   del result['formatted_address']
   del result['address_components']
   del result['types']
   #print json.dumps(result,sort_keys=True,indent=4, separators=(',', ': '))
   #result = result['geometry']
   #print json.dumps(json_obj['results'][0],sort_keys=True,indent=4, separators=(',', ': '))
   #json_obj['f']="foo"
   #print "ADDRESS:" + json.dumps(json_obj,sort_keys=True,indent=4, separators=(',', ': '))
   #print (result)
   return result

 # get geocodes from addresses
def bulk_gecode(addresses):
    res = {}
    url = 'http://maps.googleapis.com/maps/api/geocode/json'
    for address in addresses:
        # print 'fetching ' + address
        res = requests.get(url, params={
            'address': address,
            'sensor': 'false'
        })
        address = unicode(address.decode('utf8')).encode('utf8')
        res[address] = json.loads(res.content, encoding='utf8')
    return res

#fetches content of fields 195 (name), 900(address) + 902 (country) from a record, gets geo coords and encodes to a dictionary
def fetchInfoFromRecord(record):
	res = {}

	#res["type"]="feature"

	properties = {}
	geometry = {}

	libName = record.find("datafield", tag="195").find("subfield", code="a").contents[0] #195 = name
	libAddress = record.find("datafield", tag="900").find("subfield", code="a").contents[0] #900 = address
	libCountry = record.find("datafield", tag="902").find("subfield", code="a").contents[0] #902 = country

	#print libName
	#print libAddress + " " + libCountry

	properties["name"]=libName
	properties["name"]=libAddress + " " + libCountry

	geocode = get_geocode(libAddress + " " + libCountry)

	#print geocode["geometry"]["location"]

	geometry["type"]="point"
	geometry["coordinates"]=[geocode["geometry"]["location"]["lat"],geocode["geometry"]["location"]["lng"]]
	

	res["properties"]=properties
	res["geometry"]=geometry

	#print res

	return res


###########################


marcRecords = soup.find_all("record")

#print str(len(marcRecords))

#print(marcRecords)

# Data should include: Name | Address (+ country) | GIS 1 | GIS 2

if (len(marcRecords)<0):
	print("No records found - some kind of error!")
	exit

#first_record = marcRecords[0] 

#for sibling in soup.record.next_siblings:
#	fetchInfoFromRecord(sibling)

jsondict = {}

libraryList = []

for i in range(len(marcRecords)):
	libraryJSONstring = fetchInfoFromRecord(marcRecords[i])
	libraryList.append(libraryJSONstring)
	
jsondict["type"]="FeatureCollection"
jsondict["features"]=libraryList



f.write(json.dumps(jsondict,sort_keys=True,indent=4, separators=(',', ': ')))
	
f.close()






