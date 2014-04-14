#!/usr/bin/env python

import json
import collections
from lxml import html
from xml.dom.minidom import parseString

import datetime
from google.appengine.api import urlfetch
import io
from zipfile import ZipFile

from google.appengine.ext import db


def getFile():
	#file = open('conus.kml','r')
	#data = file.read()
	#file.close()

	fileData = urlfetch.fetch('http://activefiremaps.fs.fed.us/data/kml/conus.kmz')
	memfile = io.BytesIO(fileData.content)
	with ZipFile(memfile, 'r') as myzip:
	    f = myzip.open('conus.kml')
    	data = f.read()

	return data


def getName(p):
	pmName = p.getElementsByTagName('name')[0].firstChild.nodeValue
	pmName = pmName.strip()

	return pmName


def getDescription(p):
	pmDesc = p.getElementsByTagName('description')[0].firstChild.wholeText
	pmDesc = pmDesc.strip()
	
	return pmDesc


def cleanValue(pmDesc, listNum):
	keyVal = pmDesc.split('<br/>')[listNum]
	keyVal = keyVal.split(':' , 1)[1]
	keyVal = html.fromstring(keyVal).text_content()
	keyVal = keyVal.strip()
	
	return keyVal


def getDate():
        now = datetime.datetime.now()
        currentDate = now.strftime("%Y-%m-%d %H:%M:%S")

        return currentDate


def createGeoJSON(dom):
	featureList = []
	keyList = [	'latitude',
				'longitude',
				'detectionDate',
				'detectionTime',
				'confidence',
				'sensor',
				'source']

	for f in dom.getElementsByTagName('Folder'):
		folderObj = f.getElementsByTagName('name')[0]
		folderName = folderObj.firstChild.nodeValue
		folderName = str(folderName).strip()

		sixHours = '1km Fire Detection Centroids (Last 0 to 6hrs)'
		twelveHours = '1km Fire Detection Centroids (Last 6 to 12hrs)'

		if  sixHours in folderName or twelveHours in folderName:
			for p in f.getElementsByTagName('Placemark'):
				pmDesc = getDescription(p)

				entryDict = {}
				entryDict['type'] = 'Feature'

				Lat = cleanValue(pmDesc, 0)
				Lat = float(Lat)
				Lon = cleanValue(pmDesc, 1)
				Lon = float(Lon)
				coordList = [Lon, Lat]

				geoDict = {}
				geoDict['coordinates'] = coordList
				geoDict['type'] = 'Point'
				entryDict['geometry'] = geoDict

				propDict = {}
				pmType = getName(p)
				propDict['featureType'] = pmType
				
				for z in range(0,7):
					propDict[keyList[z]] = cleanValue(pmDesc, z)
				orderedProps = collections.OrderedDict(sorted(propDict.items()))
				entryDict['properties'] = orderedProps

				featureList.append(entryDict)

		geoJSON = {}
		geoJSON['type'] = 'FeatureCollection'
		currentDate = getDate()
		geoJSON['dateCreated'] = currentDate
		geoJSON['features'] = featureList
				
	jsonObj = json.dumps(geoJSON)

	return jsonObj


def errorJSON():
	regularJSON = {}
	regularJSON['error'] = 'The script encountered an error parsing the fire incident data.'
	currentDate = getDate()
	regularJSON['dateCreated'] = currentDate
	jsonObj = json.dumps(regularJSON)

	return jsonObj


class Storage(db.Model):
	jsonValue = db.BlobProperty()


def main():
	data = getFile()
	dom = parseString(data)

	try:
		content = createGeoJSON(dom)
	except:
		content = errorJSON()

	storageObj = Storage(key_name='jsonResponse',jsonValue=content)
	storageObj.put()

	print 'Content-Type: text/plain\n'
	print 'Job Complete'


if __name__ == "__main__":
	main()