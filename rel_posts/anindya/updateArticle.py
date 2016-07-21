#!/usr/bin/python

# This script fetches all the articles sequentially, checks if the article contains the sub-string supplied by the caller, removes the sub-string from the article and stores it back.
# Argument1: Sub-string to be deleted.

import os
import sys
from sys import argv
script, substr = argv

import psycopg2 # for PostgreSQL

def main():

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

	# Open a connection to the database
	try:
		conn = psycopg2.connect(database=credentials['database'], user=credentials['user'], password=credentials['password'], host=credentials['host'], port=credentials['port'])
	except:
		print "Unable to connect to the database."
		print "Unexpected error:", sys.exc_info()[0]
		raise

	cursor1 = conn.cursor()
	cursor2 = conn.cursor()

	query = "SELECT table_key FROM all_posts"

	# fetch the primary key
	try:
		cursor1.execute(query)
	except:
		print "Failed to execute the query."
		print "Unexpected error:", sys.exc_info()[0]
		raise

	match_count = 0
	for ctr,row in enumerate(cursor1.fetchall()):
		print ctr+1,row[0]
		query = "SELECT article FROM all_posts WHERE table_key = %d" % int(row[0])
		
		try:
			cursor2.execute(query)
		except:
			print "Failed to execute the query."
			print "Unexpected error:", sys.exc_info()[0]
			raise

		article = cursor2.fetchone()[0]
		
		if substr in article:
			match_count = match_count + 1
			article = article.replace(substr, "")

		# this is for debugging purposes
		query = "UPDATE all_posts SET article = %s WHERE table_key = %s" % (article, row[0])
		# update the row
		try:
			cursor2.execute("UPDATE all_posts SET article = %s WHERE table_key = %s",(article, row[0])) # can't pass integers here
		except:
			print "Failed to execute the query."
			print "Unexpected error:", sys.exc_info()[0]
			raise

	print "Total matches found:",match_count

	cursor2.close()
	cursor1.close()
	conn.commit()
	conn.close()
	return

if __name__ == "__main__": main()
