#!/usr/bin/env python

# Justin Ashworth 2008

# to do:
# google maps...

print 'Content-type: text/html'

import cgi
import cgitb; cgitb.enable()

print '''
<!--Justin Ashworth 2008-->
<!--all code is original unless noted otherwise.-->
<!--Permission to use the content in this page (and its children) for business purposes without agreement of the author is strictly denied.-->
<html>
<head>
<link rel="stylesheet" type="text/css" href="style.css">
<!-- javascript includes -->
</head>
<body>
'''

form = cgi.FieldStorage()

area = 'seattle'
area = form.getvalue('area')
if area == '' or area == None: area = 'seattle'

searchstring = form.getvalue('searchstring')
if searchstring == None: searchstring = ''
import re
searchstring = re.sub('\s+','+',searchstring)

minprice = 0; maxprice = 0
try: minprice = int(form.getvalue('minprice'))
except: pass
try: maxprice = int(form.getvalue('maxprice'))
except: pass

category = form.getvalue('catAbbreviation')
if category == None: category = 'sss'

categories = [
	('sss','for sale'),
	('hhh','housing'),
	('ccc','community'),
	('eee','events'),
	('ggg','gigs'),
	('jjj','jobs'),
	('ppp','personals'),
	('res','resumes'),
	('bbb','services')
]

sublocation = form.getvalue('sublocation')
if sublocation == None: sublocation = 'all'

sublocations = {
	'seattle' : [
		('all','all'),
		('see','seattle'),
		('est','eastside'),
		('sno','snohomish co'),
		('kit','kitsap co'),
		('tac','tacoma'),
		('oly','olympia'),
		('skc','south king')
	]
}

craigslist = 'http://%s.craigslist.org/search/%s' %(area,category)
if sublocation != 'all': craigslist += '/%s' %sublocation
query = '%s?query=%s&minAsk=%i&maxAsk=%i&hasPic=1' %(craigslist,searchstring,minprice,maxprice)


import urllib
import sys
results = ''
try: results = urllib.urlopen(query).read()
except:
	print '<font color="#FF0000">Error: url does not exist (non-existent location specified...?)</font><br><br>'
#	print '</body></html>'; sys.exit()

class Listing:
	def __init__(self,date,url,title,price,location):
		self.date = date
		self.url = url
		self.title = title
		self.price = price
		self.location = location
		#self.url = 'http://%s.craigslist.org%s' %(area,self.url)
		self.pics = []
		self.fetch_details()

	def fetch_details(self):
		listing = urllib.urlopen(self.url).read()
		re_pic = re.compile('<img src="(http://images.craigslist.org/[^"]+)"')
		for pic in re_pic.finditer(listing):
			self.pics.append( pic.groups()[0] )
		self.streets = None
		self.google = None
		re_streets_and_google = re.compile('<br><br>([^<]+)<font[^>]+><a target="[^"]+" href="(http://maps.google.com[^>]+)>')
		match = re_streets_and_google.search(listing)
		if match == None: return
		self.streets, self.google = match.groups()

listings = []
# stupid f'ing craigslist: summary listing format depends on category
re_listing = None

if category == 'hhh':
	# groups: ( date, url, price, title, location )
	re_listing = re.compile('<p>([^<]+)<a href="([^"]+)">\$([^\s<]+)\s+([^<]+)</a><font size="-1">([^<]+)</font>')
elif category == 'ccc':
	# groups: ( date, url, title, location )
	re_listing = re.compile('<p>([^<]+)<a href="([^"]+)">([^<]+)</a>[^<]+<font size="-1">([^<]+)</font>')

else:
	# groups: ( date, url, title, price, location )
	#re_listing = re.compile('<p>([^<]+)<a href="([^"]+)">([^\$<]+)\$([^ <-]+)[^<]+</a><font size="-1">([^<]+)</font>')
	# groups: date, url, title, price, location
	re_listing = re.compile('<span class="itemdate">([^<]+)<.+?<a href="(http://[^"]+)">([^<]+)<.+?<span class="itempp">([^>]+)<.+?(\([^\)]+\))',re.DOTALL)

for listing in re_listing.finditer(results):
	price = None
	if category == 'hhh':
		date, url, price, title, location = listing.groups()
	elif category == 'ccc':
		date, url, title, location = listing.groups()
	else:
		date, url, title, price, location = listing.groups()
	if price:
		price = re.sub('\(|\)|\$|,|\'|!','',price)
	if price == '': price = 0.0
	try: price = float(price)
	except: price = 0.0
	listings.append( Listing(date,url,title,price,location) )

print 'Last search url: <a href="%s" target="_blank">%s</a><br><br>' %(query,query)
print '''
<form action="index.cgi" method="post">
	Area: <input type="text" name="area" value="%s"/>''' %area

if not sublocations.has_key(area):
	sublocations[area] = [ ('all','all') ]
print	'Sublocation: <select name="sublocation">'
for loccode,name in sublocations[area]:
	line = '\t\t<option value="%s"' %loccode
	if loccode == sublocation:
		line += ' selected="selected"'
	line += '>%s' %name
	print line
print '</select>'
print '<br><br>'

print 'Search string: <input type="text" name="searchstring" value="%s"/>' %searchstring

print ' <select name="catAbbreviation">'
for catcode,name in categories:
	line = '\t\t<option value="%s"' %catcode
	if catcode == category:
		line += ' selected="selected"'
	line += '>%s' %name
	print line
print '</select><br><br>'

print '''
Price min: <input type="text" name="minprice" value="%i"/>
max: <input type="text" name="maxprice" value="%i"/><br><br>
''' %( minprice, maxprice )

print '<input type="submit" value="Search"></form>'
print 'Number of listings found: %i<br><br>' %( len(listings) )

import string
for listing in listings:
	print '%s - <a href="%s">%s</a> - %s - $%s<br>' \
		%( listing.date, listing.url, listing.title, listing.location, listing.price )
	if listing.streets != None: print '%s' %listing.streets
	if listing.google != None: print ' <a href="%s" target="_blank">google</a>' %listing.google
	print '<br>'
	for pic in listing.pics:
		print '<img src="%s">' %pic
	print '<br><br>'

print '''
</body></html>
'''
