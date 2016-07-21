import psycopg2

try:
    conn = psycopg2.connect(" dbname='yashgoel2' user='yashgoel2' host='localhost' password='yashgoel123' ")
    print "Hey!"
except:
    print "I am unable to connect to the database"
