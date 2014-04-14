#!/usr/bin/env python

import webapp2
from google.appengine.ext import db


class Storage(db.Model):
	jsonValue = db.BlobProperty()


class MainHandler(webapp2.RequestHandler):
	def get(self):
		storageObj = db.Key.from_path('Storage', 'jsonResponse')
		data = db.get(storageObj).jsonValue
		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(data)


app = webapp2.WSGIApplication([('/', MainHandler)], debug=True)