#!/usr/bin/python

# This script searches the supplied query in the local database
# Argument: The search query to be made

from sys import argv
script, search_query = argv

import sys
import psycopg2

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

	query = "SELECT table_key, url, topic FROM all_posts WHERE to_tsvector('english', article) @@ plainto_tsquery('english', \'%s\')" % search_query
	# print query

	# perform full text search
	try:
		cur.execute(query)
	except:
		print "Failed to search the database."
		print "Unexpected error:", sys.exc_info()[0]
		raise

	result_cnt = 0
	for ctr,row in enumerate(cur.fetchall()):
		if row[2] is not 19: # check if it's not an interview experience
			result_cnt = result_cnt + 1
			print ctr+1, row[0], row[1], row[2]

		if result_cnt == 5:
			break;

	cur.close()
	conn.close()
	return

if __name__ == "__main__": main()
