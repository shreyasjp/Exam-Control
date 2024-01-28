import mysql.connector as a

b = a.connect(host='localhost', user='root', passwd='root')
d = b.cursor(buffered=True)

subs = {}  # Dictionary to store PRN:Subject pairs
prn = []   # List of all students

# Fetch room details from database
""" d.execute('SELECT * FROM test.rooms JOIN test.room_class_specs ON test.rooms.RoomClassID = test.room_class_specs.RoomClassID;')
rooms = []  # List of all rooms and their specifications """

# Fetch subject details from database
d.execute('SELECT * FROM test.prn_sub;')
e = d.column_names
f = list(e)  # List of all subjects
f.pop(0)     # Remove Sl. No 

for subject in f:
    create_table_query = f'CREATE TABLE IF NOT EXISTS students.`{subject}` (sl_no INT AUTO_INCREMENT PRIMARY KEY, class_no INT, prn BIGINT NOT NULL UNIQUE, mame VARCHAR(255));'
    d.execute(create_table_query)

    select_data_query = f'SELECT `{subject}` FROM test.prn_sub WHERE `{subject}` IS NOT NULL;'
    d.execute(select_data_query)
    rows = d.rowcount
    selected_data = d.fetchall()

    for row in selected_data:
        prn_value = row[0]
        subs[prn_value] = subject
        prn.append(prn_value)

        insert_data_query = f'INSERT INTO students.`{subject}` (PRN) VALUES ({prn_value});'
        d.execute(insert_data_query)
        b.commit()

    print('Table', subject, 'updated')

# Commit changes
b.commit()
