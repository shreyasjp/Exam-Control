import csv
import mysql.connector

""" def fix_string(text):
    if 'Finance & Taxation' in text:
        return 'B.Com Model I Finance & Taxation'
    if text[:5] == 'B.Com':
        return text[:5]+text[6:]
    else:
        return text """

# Connect to the database
db = mysql.connector.connect(user="root", password="root", host="localhost", database="exam_cell_data")
cursor = db.cursor()

students = []

""" with open('UG2021.csv', 'r') as file:
    reader = csv.reader(file)
    prn = []
    for row in reader:
        if row[3] != '' and row[3] != '#N/A' and row[2] != '' and row[2] != 'Candidate Name' and row[9] != '':
            if row[3] not in prn:
                prn.append(row[3])
            else:
                continue
            students.append({
                'prn': str(row[3]),
                'name': str(row[2]).replace("'", "\\'"),
                'level': 'UG',
                'program': fix_string(str(row[9])),
                'batch': f'20{str(row[3])[:2]}',
            })

with open('UG2022.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if row[3] != '' and row[3] != '#N/A' and row[2] != '' and row[2] != 'Candidate Name' and row[10] != '':
            if row[3] not in prn:
                prn.append(row[3])
            else:
                continue
            students.append({
                'prn': str(row[3]),
                'name': str(row[2]).replace("'", "\\'"),
                'level': 'UG',
                'program': str(row[10]),
                'batch': f'20{str(row[3])[:2]}',
            })

print(students)
print(len(students))

# Insert student data into the student table
for student in students:
    query = f"INSERT INTO students (prn, name, level, program, batch) VALUES ('{student['prn']}', '{student['name']}', '{student['level']}', '{student['program']}', '{student['batch']}')"
    a = cursor.execute(query)

# Commit the changes to the database
db.commit()

# Close the database connection
db.close()
"""

departments = []

with open('Teachers.csv', 'r') as file:
    reader = csv.reader(file)
    teachers_id = []
    teachers_name = []
    teachers = []
    for row in reader:
        if row[0] not in teachers_id and row[1].strip()[4:] not in teachers_name:
            teachers_id.append(row[0])
            teachers_name.append(row[1].strip()[4:])
            teachers.append({'ID': row[0], 'Name': row[1].strip()[4:], 'Department': row[2]})
        if row[2] not in departments:
            departments.append(row[2])

print(teachers)

for student in teachers:
    query = f"INSERT INTO teachers (teacher_id, name, department, date_of_joining) VALUES ('{student['ID']}', '{student['Name']}', '{student['Department']}', '11/09/2001')"
    a = cursor.execute(query)

# Commit the changes to the database
db.commit()

# Close the database connection
db.close()