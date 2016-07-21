#!/usr/bin/python

# This script returns Text Search statistics for Interview Experiences ordered first by nentry(no. of entries) and then by ndoc(no. of documents) with limit imposed on the number of results.
# Argument: Result Limit

import os
import sys
from sys import argv
script, limit = argv

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

	cur = conn.cursor()

	query = "SELECT * FROM ts_stat('SELECT to_tsvector(article) FROM all_posts WHERE topic = 19') ORDER BY nentry DESC, ndoc DESC, word LIMIT %d" % int(limit)

	# fetch the articles from the database for this topic, restrict the results with limit
	try:
		cur.execute(query)
	except:
		print "Failed to execute the query."
		print "Unexpected error:", sys.exc_info()[0]
		raise

	for ctr,row in enumerate(cur.fetchall()):
		print ctr+1,row[2],row[1],row[0]

	cur.close()
	conn.close()
	return

if __name__ == "__main__": main()
