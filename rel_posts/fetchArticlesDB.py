#!/usr/bin/python
# encoding=utf8
# This script returns the requested number (limit) of articles from our local Database for the requested category.
# Argument1: Category Number
# Argument2: Result Limit

import os
import sys
from sys import argv
script, category, limit = argv
from nltk.corpus import stopwords
from nltk import word_tokenize
import psycopg2 # for PostgreSQL
#reload(sys)
#sys.setdefaultencoding("utf-8")
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

	query = "SELECT * FROM all_posts WHERE topic = %d LIMIT %d" % (int(category), int(limit))

	# fetch the articles from the database for this topic, restrict the results with limit
	try:
		cur.execute(query)
	except:
		print "Failed to execute the query."
		print "Unexpected error:", sys.exc_info()[0]
		raise
        d = {}
        dict1 = {}
	for ctr,row in enumerate(cur.fetchall()):
		list1 = [row[0],row[1],row[2],row[3],row[4]]
		dc=row[3].decode('utf8')
		print ctr+1,"\n",row[2]
		print type(dc)
                #dc=unicode(dc,errors='ignore')
                list2 = word_tokenize(dc)
                #print list2
                list3 = [w for w in list2 if w not in stopwords.words('english')]
                #print list3
                for i in list3:
                    key=i
                    if key in d:
                        d[key] += 1
                    else:
                        d[key] = 1
                dict1[ctr+1] = d.copy()
                print dict1[ctr+1]
               
		query2 = "UPDATE all_posts SET category_id=%d WHERE table_key=%d" % (ctr+1,row[0])
                cur.execute(query2)
                d.clear()
                print "********************************************************************************************************************************************************************"
        print ctr 
        l={}
        '''for i in xrange(1,ctr+2):
            for j in xrange(1,ctr+2):
                if (i==j):
                   print i,j
                   continue
                print i,j      
                aftermerging= { x:min(dict1[i][x],dict1[j][x]) for x in set(dict1[i]) & set(dict1[j]) }
                print aftermerging
                l[i]={j: sum(aftermerging.values())}
                aftermerging.clear()
                print l[i][j]'''
             
	cur.close()
	conn.close()
	return


if __name__ == "__main__": main()
