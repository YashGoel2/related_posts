#!/usr/bin/python

# This script returns the QAs for the supplied interview experience URL.
# Argument1: interview experience URL

import os
import sys
from sys import argv
script, queUrl = argv

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

	# this is for debugging purposes
	query = "SELECT company, question, url FROM all_posts RIGHT OUTER JOIN possible_qa ON (possible_qa.answer_key = all_posts.table_key) WHERE question_key = (SELECT table_key FROM all_posts WHERE url = \'%s\')" % queUrl

	# fetch the articles from the database for this topic, restrict the results with limit
	try:
		cur.execute(query)
	except:
		print "Failed to execute the query."
		print "Unexpected error:", sys.exc_info()[0]
		raise

	for ctr,row in enumerate(cur.fetchall()):
		print ctr+1, row

	cur.close()
	conn.close()
	return

if __name__ == "__main__": main()
