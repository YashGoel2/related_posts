#!/usr/bin/python

# This is an evolving script! *.*

from bs4 import BeautifulSoup
import requests
import os
import sys
import psycopg2

conn = None
cur = None

catUrls = {1:"http://www.geeksforgeeks.org/category/advanced-data-structure/",
	2:"http://www.geeksforgeeks.org/category/algorithm/",
	3:"http://www.geeksforgeeks.org/category/algorithm/analysis/",
	4:"http://www.geeksforgeeks.org/category/c-arrays/",
	5:"http://www.geeksforgeeks.org/category/articles/",
	6:"http://www.geeksforgeeks.org/category/algorithm/backtracking/",
	7:"http://www.geeksforgeeks.org/category/binary-search-tree/",
	8:"http://www.geeksforgeeks.org/category/bit-magic/",
	9:"http://www.geeksforgeeks.org/category/c-puzzles/",
	10:"http://www.geeksforgeeks.org/category/algorithm/divide-and-conquer/",
	11:"http://www.geeksforgeeks.org/category/algorithm/dynamic-programming/",
	12:"http://www.geeksforgeeks.org/category/guestblogs/",
	13:"http://www.geeksforgeeks.org/category/algorithm/geometric/",
	14:"http://www.geeksforgeeks.org/category/gfact/",
	15:"http://www.geeksforgeeks.org/category/graph/",
	16:"http://www.geeksforgeeks.org/category/algorithm/greedy/",
	17:"http://www.geeksforgeeks.org/category/hash/",
	18:"http://www.geeksforgeeks.org/category/heap/",
	19:"http://www.geeksforgeeks.org/category/interview-experiences/",
	20:"http://www.geeksforgeeks.org/category/java/",
	21:"http://www.geeksforgeeks.org/category/linked-list/",
	22:"http://www.geeksforgeeks.org/category/algorithm/mathematical/",
	23:"http://www.geeksforgeeks.org/category/matrix/",
	24:"http://www.geeksforgeeks.org/category/multiple-choice-question/",
	25:"http://www.geeksforgeeks.org/category/c-programs/",
	26:"http://www.geeksforgeeks.org/category/program-output/",
	27:"http://www.geeksforgeeks.org/category/algorithm/pattern-searching/",
	28:"http://www.geeksforgeeks.org/category/project/",
	29:"http://www.geeksforgeeks.org/category/queue/",
	30:"http://www.geeksforgeeks.org/category/algorithm/randomized/",
	31:"http://www.geeksforgeeks.org/category/algorithm/searching/",
	32:"http://www.geeksforgeeks.org/category/algorithm/sorting/",
	33:"http://www.geeksforgeeks.org/category/stack/",
	34:"http://www.geeksforgeeks.org/category/c-strings/",
	35:"http://www.geeksforgeeks.org/category/tree/",
	}


def main():
	global conn
	global cur

	# Read the credentials.secret file
	credentials = {}
	# The credentials.secret file contains the required infromation to connect to the database.
	with open("credentials.secret") as f:
		for line in f:
			if line.startswith('#'):
				continue
			(key, val) = line.split('=')
			val = val.rstrip()
			credentials[key] = val

	try:
		conn = psycopg2.connect(database=credentials['database'], user=credentials['user'], password=credentials['password'], host=credentials['host'], port=credentials['port'])
	except:
		print "Unable to connect to the database."
		print "Unexpected error:", sys.exc_info()[0]
		raise

	cur = conn.cursor()

	createTable() # This creates one table that will store all the posts
	processCategories() # This will process all the categories iteratively

	cur.close() # Close the cursor
	conn.close() # Close the connection. (How to check if it's closed?)
	return

# This method lists the categories on GfG
def processCategories():
	for key in catUrls.keys():
		url = catUrls[key]
		print key, url
		processCategoryUrls(key, url)
	return

# This method processes all the Urls under a certain category
# Parameters: 
# topic(int): category number to be stored in the database
# url(str): url of the category which to process
def processCategoryUrls(topic, url):
	r = requests.get(url)
	data = r.text
	soup = BeautifulSoup(data)
	span = soup.find('span', {"class":"pages"})
	pageCount = 0
	if span is not None:
		pageCount = int(span.text.rsplit(' ',1)[-1])

	# process page 0
	print '\t','0',topic,url
	dbdump(topic, url)

	if pageCount == 0:
		return

	# process other pages in a loop
	for i in range(2,pageCount):
		nextUrl = url + "page/" + str(i) + "/"
		print '\t',i,topic,nextUrl
		dbdump(topic, nextUrl)
	return

# This method finds all the URLs on a Category page, fetches the corresponding article and dumps them in the database.
# Parameter1: URL for any Category page e.g. http://www.geeksforgeeks.org/category/stack/ or http://www.geeksforgeeks.org/category/stack/page/2/
# Parameter2: Topic no. for that category
def dbdump(topic, url):
	global conn
	global cur

	# url is now received as a parameter
	# url = first # pass the url via command line
	r = requests.get(url)
	data = r.text
	soup = BeautifulSoup(data)

	# This snippet processes all the URLs
	for ctr,art in enumerate(soup.find_all('article')):
		a = art.find('a', href=True)
		print "\t", ctr+1, a['href']
		url = a['href']
		title = a.text
		article = fetchArticle (a['href'])

		# this is for debugging purposes
		query = "INSERT INTO all_posts(url, title, article, topic) VALUES (%s, %s, %s, %s)" % (url, title, article, topic)
		# dump the article into the database
		try:
			cur.execute("INSERT INTO all_posts(url, title, article, topic) VALUES (%s, %s, %s, %s)", (url, title, article, topic))
		except:
			print "Failed to insert into all_posts. Query:", query
			print "Unexpected error:", sys.exc_info()[0]
			raise
	
	conn.commit()
	return

# This method fetches/scrapes the article from the supplied URL.
# Parameter: URL for a GFG-Article page
def fetchArticle (url):
	r  = requests.get(url)
	data = r.text
	soup = BeautifulSoup(data)

	[tag.decompose() for tag in soup("script")] # Removing any scripts
	[tag.decompose() for tag in soup("footer")] # Removing the footer

	art = soup.article
	for pre in art.find_all('pre'):
		if pre.has_attr('class'):
			pre.decompose()

	result = art.text.strip()
	# print result # This data should go into the text column of the Database Table
	return result

# This creates one table that will store all the posts
def createTable():
	global conn
	global cur
	query = """CREATE TABLE IF NOT EXISTS all_posts (table_key SERIAL PRIMARY KEY, url VARCHAR(240), title VARCHAR(160), article TEXT, topic SMALLINT);"""
	try:
		cur.execute(query)
	except:
		print "Unable to create table 'all_posts'."
		print "Unexpected error:", sys.exc_info()[0]
		raise

	conn.commit()
	return

if __name__ == "__main__": main()
