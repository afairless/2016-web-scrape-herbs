#! /usr/bin/env python3

'''
Andrew Fairless
January 2016

This program downloads information on herbs and supplements listed by the U. S. 
National Library of Medicine (NLM).  The NLM webpage lists herbs and supplements 
from several sources; this program downloads only fact sheets (in 'pdf' format)
from the National Center for Complementary and Integrative Health (NCCIH).  The
fact sheets are saved in a new directory created in the present working directory.

This program also saves a list of the herbs and supplements for which fact sheets
were downloaded.  The list is saved in a text file in the same directory where
the fact sheets are saved.

The purpose of this project was to let me learn and practice web scraping and 
Python programming.  Much of the code is based on Chapter 11 ('Web Scraping') of 
'Automate the Boring Stuff' by Al Sweigart:
https://automatetheboringstuff.com/chapter11/
'''


import requests, bs4, re, os, time


def getwebrequest(url):
	'''
	gets file from internet location specified by 'url'
	returns file in form of 'requests' object
	requires 'requests' package
	'''
	res = requests.get(url)				# download webpage

	# checks for error; error does not halt program; prints error message instead
	try:
		res.raise_for_status()
	except Exception as exc:
		print('There was a problem: %s' % (exc))

	return(res)


def getwebpagesoup(url):
	'''
	gets webpage 'html' file from internet location specified by 'url'
	returns parsed 'html' file for easy retrieval of 'html' elements in file
	requires 'requests' and 'beautifulsoup' ('bs4') packages
	calls 'getwebrequest' function
	'''
	res = getwebrequest(url)
	soup = bs4.BeautifulSoup(res.text, "lxml")	# parses html
	return(soup)


def writewebrequesttofile(webrequest, filepathname, openmode = 'wb'):
	'''
	saves download ('webrequest') to a file with location specified by 'filepathname')
	in case download file size is large, writing in chunks limits memory usage
	requires 'requests' package
	'''
	writethisfile = open(filepathname, mode = openmode)
	for chunk in res.iter_content(100000):
		writethisfile.write(chunk)
	writethisfile.close()
	

herbdirname = 'nccihherbfactsheets'		# directory to store downloaded files
os.makedirs(herbdirname, exist_ok = True)	

# webpage from NLM listing herbs and supplements and weblinks for further information
pageurl = 'https://www.nlm.nih.gov/medlineplus/druginfo/herb_All.html' 
pagesoup = getwebpagesoup(pageurl)

# each element corresponds to an NLM-listed herb or supplement
herblistelem = pagesoup.select('section a')	

urlstart = "https://nccih.nih.gov"
herbs = []		# herb and supplement names 


# for each NLM-listed herb or supplement
for elem in range(len(herblistelem)):
	herburl = herblistelem[elem].get('href')	# extracts weblink

	# if source of weblink for further information is NCCIH
	if bool(re.search(urlstart, herburl)):
		herbs.append(herblistelem[elem].string)
		herburlsoup = getwebpagesoup(herburl)

		# identifies fact sheet URL
		elem = herburlsoup.select('ul[class="fslisticons"] a')[0]
		pdfurl = urlstart + elem.get('href')

		time.sleep(5)			# delay to avoid burdening server

		print('Downloading information about %s from %s' % (herbs[-1], pdfurl))
		res = getwebrequest(pdfurl)	# download fact sheet 'pdf' file
		filepathname = os.path.join(herbdirname, os.path.basename(pdfurl))
		writewebrequesttofile(res, filepathname, 'wb')	# save 'pdf' file

		time.sleep(10)			# delay to avoid burdening server


# save list of herbs and supplements in same directory that stores fact sheets
herblistfilepathname = os.path.join(herbdirname, "herblist.txt")
with open(herblistfilepathname, mode = 'w', encoding = 'utf-8') as textstream:
	textstream.write("Information was downloaded about the following herbs and supplements:\n")
	for iter in range(len(herbs)):
		textstream.write(herbs[iter])
		textstream.write("\n")

