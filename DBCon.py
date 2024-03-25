import mysql.connector

# Creating DB connection
CON = mysql.connector.connect(host="localhost", user="root", password="root", database='exam_cell_data')
DB = CON.cursor(buffered=True)