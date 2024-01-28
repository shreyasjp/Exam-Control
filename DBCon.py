import mysql.connector

# Creating DB connection
CON = mysql.connector.connect(host="localhost", user="root", password="root")
DB = CON.cursor(buffered=True)