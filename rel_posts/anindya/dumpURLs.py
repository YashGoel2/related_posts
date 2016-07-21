#!/usr/bin/python

# This script dumps all the URLs, their Titles and their Category into a csv file
# Argument: Category

from sys import argv
script, category = argv

import csv
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

	query = "SELECT table_key, url, title, topic FROM all_posts WHERE topic = %d" % (int(category))
	# print query

	# dump them in the csv file
	try:
		cur.execute(query)
	except:
		print "Failed to fetch from the database."
		print "Unexpected error:", sys.exc_info()[0]
		raise

	with open('URLs.csv', 'wb') as csvfile:
		urlwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		for ctr,row in enumerate(cur.fetchall()):
			print ctr+1, row[0], row[1], row[2], row[3]
			urlwriter.writerow([ctr, row[0], row[1], row[2], row[3]])

	cur.close()
	conn.close()
	return

if __name__ == "__main__": main()

