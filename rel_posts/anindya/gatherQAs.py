#!/usr/bin/python

# This script extracts possible questions from interview experiences and looks for possible answer in other articles. Limit (user supplied) decides the number of interviews to go through.
# Argument1: Result Limit

import os
import sys
from sys import argv
script, limit = argv

import psycopg2 # for PostgreSQL
import re, string

conn = None

def main():
	global conn

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

	createTable() # This creates a table that will store the extracted questions and answers
	processInterviews() # This method processes the interview experiences for QAs

	conn.close()
	return

# This method processes the interview experiences for QAs
def processInterviews():
	global conn
	cur = conn.cursor()

	# fetch the interview experiences from the database, restrict the results with limit
	query = "SELECT table_key, title, article FROM all_posts WHERE topic = 19 LIMIT %d" % int(limit)
	try:
		cur.execute(query)
	except:
		print "Failed to execute the query."
		print "Unexpected error:", sys.exc_info()[0]
		raise

	for ctr,row in enumerate(cur.fetchall()):
		# Prints the details of the current interview experience being processed.
		print ctr+1,row[0],row[1]
		queList = extractQuestions(row[2]) # This method extracts possible questions from the supplied article
		company = extractCompany(row[1].lower())
		processQuestions(row[0], company, queList) # This method processes the supplied questions
	
	cur.close()
	return

# This method finds answers for the supplied questions
def processQuestions(queKey, company, queList):
	# every subList is a multi-part question
	for idx, partList in enumerate(queList):
		# print partList
		question = ' | '.join(partList)
		answerSet = findAnswers(partList) # This method finds answers for the supplied questions
		if not answerSet:
			# we still have to save the unanswered questions in the database
			storeQAs(queKey, -1, company, question)
		for ansKey in answerSet:
			# print '\t', ansKey, answerSet[key]
			storeQAs(queKey, ansKey, company, question)
	return

# This method dumps the extracted QAs into the database
def storeQAs(queKey, ansKey, company, question):
	global conn
	cur = conn.cursor()

	# this is for debugging purposes
	query = "INSERT INTO possible_qa(question_key, answer_key, company, question) VALUES (%s, %s, %s, %s)" % (queKey, ansKey, company, question)
	try:
		cur.execute("INSERT INTO possible_qa(question_key, answer_key, company, question) VALUES (%s, %s, %s, %s)", (queKey, ansKey, company, question))
	except:
		print "Failed to execute the query."
		print "Unexpected error:", sys.exc_info()[0]
		raise
	
	cur.close()
	conn.commit()
	return

# This method finds answers for the supplied questions
def findAnswers(question):
	global conn
	cur = conn.cursor()

	answerSet = {}
	for part in question:
		# print idx+1, part

		query = "SELECT table_key, url, topic FROM all_posts WHERE to_tsvector('english', article) @@ plainto_tsquery('english', \'%s\')" % part
		# perform full text search
		try:
			cur.execute(query)
		except:
			print "Failed to search the database."
			print "Unexpected error:", sys.exc_info()[0]
			raise

		result_cnt = 0
		for ctr, row in enumerate(cur.fetchall()):
			if row[2] is not 19:
				# print '\t', ctr+1, row[0], row[1]
				if row[0] not in answerSet:
					answerSet[row[0]] = row[1]
					result_cnt = result_cnt + 1
			# atmost 5 urls should be enough
			if result_cnt == 5:
				break;
	
	cur.close()
	return answerSet

# This method extracts the company name from the supplied title
def extractCompany(title):
	company = None
	begins = ['synopsys','yatra','deloitte','rockwell collins','opera solutions','service now','spire technologies','wow labz','alcatel lucent','swiggy','infinera','optimus information inc.','indus valley partners','samsung research institute','bankbazaar.com','sri','d. e. shaw & co.','compro technologies']
	singles = ['directi', 'browserstack', 'microsoft']
	doubles = ['national instruments', 'mentor graphics', 'bharti softbank']

	end = title.find('toptalent')
	if end is not -1:
		company = 'toptalent'
	else:
		match = [ x for x in begins if title.startswith('interview') and x in title ]
		if not match:
			end = title.find(' interview')
			if end is not -1:
				company = title[:end]
			else:
				end = title.find(' on')
				if end is not -1:
					company = title[:end]
				else:
					end = title.find(' placement')
					if end is not -1:
						company = title[:end]
					else:
						end = title.find(' recruitment')
						if end is not -1:
							company = title[:end]
						else:
							end = title.find('ibibo/zoomcar')
							if end is not -1:
								company = 'ibibo zoomcar'
							else:
								match = [ x for x in singles if x in title ]
								if not match:
									match = [ x for x in doubles if x in title ]
									if not match:
										if '10 most asked questions from java programmers' in title:
											company = '10 most asked questions from java programmers'
										elif 'payu' in title:
											company = 'payu'
										else:
											company = None
									else:
										company = match[0]
								else:
									company = match[0]
		else:
			company = match[0]
	return company

# This method extracts possible questions from the supplied article
def extractQuestions(article):
	# keywords = ['find', 'write','explain'] # tried many combos. makes things complex.
	keywords = ['find', 'write']
	queList = [] # the list of questions to be returned. every subList inside this list reprent one question.

	pattern = re.compile('[\.\.]+')
	article = pattern.sub('.', article) # replacing more than one dots with a single dot

	pattern1 = re.compile('[^A-Za-z0-9\. ]+') # for stripping evertyhing except alphanumeric characters
	pattern2 = re.compile('[\s\s]+') # for removing multiple spaces
	for line in article.split('\n'):
		for word in keywords:
			if word in line:
				start = line.index(word) + len(word)
				end = line.rfind('.', start)
				# print start, end, len(line)
				if end > start:
					result = line[start:end]
				else:
					result = line[start:]
				result = pattern1.sub(' ', result) # strip non-alphanumeric, non-space and non-dot characters
				result = pattern2.sub(' ', result)

				subList = result.split('.')
				subList[:] = [item.strip() for item in subList]

				queList.append(subList)
				break # match atmost one keyword per line
	return queList

# This creates a table that will store the extracted questions and answers
def createTable():
	global conn

	cur = conn.cursor()
	query = """CREATE TABLE IF NOT EXISTS possible_qa (table_key SERIAL PRIMARY KEY, question_key INTEGER, answer_key INTEGER, company VARCHAR(50), question TEXT);"""
	try:
		cur.execute(query)
	except:
		print "Unable to create table 'all_posts'."
		print "Unexpected error:", sys.exc_info()[0]
		raise

	cur.close()
	conn.commit()
	return

if __name__ == "__main__": main()
