#!/usr/bin/python

# This script returns local keywords for interview experiences sequentially.
# Argument1: Result Limit - Records
# Argument2: Result Limit - Words

import os
import sys
from sys import argv
script, limit1, limit2 = argv

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

	query = "SELECT table_key FROM all_posts WHERE topic = 19 LIMIT %d" % int(limit1)

	# fetch the primary key, restricts the number of results with the requested limit
	try:
		cursor1.execute(query)
	except:
		print "Failed to execute the query."
		print "Unexpected error:", sys.exc_info()[0]
		raise

	for ctr,row in enumerate(cursor1.fetchall()):
		print ctr+1,row[0]

		query = "SELECT * FROM ts_stat(\'SELECT to_tsvector(article) FROM all_posts WHERE table_key = %d\') ORDER BY nentry DESC, ndoc DESC, word LIMIT %d" % (int(row[0]), int(limit2))
		try:
			cursor2.execute(query)
		except:
			print "Failed to execute the query."
			print "Unexpected error:", sys.exc_info()[0]
			raise	
		
		for ctr,row in enumerate(cursor2.fetchall()):
			print ctr+1,row[2],row[1],row[0]

	cursor2.close()
	cursor1.close()
	conn.close()
	return

if __name__ == "__main__": main()
