import random
import DBCon

# Define the RoomInfo class
class RoomInfo:
    def __init__(self, name, seats, columns, rows):
        self.Name = name
        self.Seats = seats
        self.Columns = columns
        self.Rows = rows
        self.Seating = []
        self.SeatsFilled = 0

# Connect to the database
DB = DBCon.DB

# Get the list of tables from the database
DB.execute("SHOW TABLES FROM students ;")
tables = DB.fetchall()
Subs = tables
Student_Sub_Dict = {}

# Create a dictionary to map student IDs to subjects
for table_info in tables:
    table_name = table_info[0]

    DB.execute(f"SELECT prn FROM students.{table_name};")
    student_ids = DB.fetchall()

    for student_id in student_ids:
        Student_Sub_Dict[student_id[0]] = table_name

# Calculate the total number of students per subject
TotalStudentsPerSub = {}
StudentsperSub = {}

for i in Subs[1:]:
    TotalStudentsPerSub[i] = len([k for k, v in Student_Sub_Dict.items() if v == i])
    StudentsperSub[i] = [k for k, v in Student_Sub_Dict.items() if v == i]

TotalStudents = len(Student_Sub_Dict)

# Get the room data from the database
DB.execute('SELECT room_data.rooms.room_name, room_data.room_class_specs.seats, room_data.room_class_specs.columns, room_data.room_class_specs.rows FROM room_data.rooms JOIN room_data.room_class_specs ON room_data.rooms.room_class_id = room_data.room_class_specs.room_class_id;')
RoomData = DB.fetchall()

# Create RoomInfo objects for each room
for i in RoomData:
    RoomData[RoomData.index(i)] = RoomInfo(i[0], i[1], i[2], i[3])

# Find the required rooms based on the total number of students
RequiredRooms = []
MaxCapacity = sum(i.Seats for i in RoomData)

RequiredSeats = TotalStudents
AllotedSeats = 0

flag = 0

# Allocate rooms based on the number of seats required
if RequiredSeats > MaxCapacity:
    print("Hail Hitler")
else:
    if RequiredSeats < 16:
        RequiredRooms.append(RoomData[-1])
        AllotedSeats += RoomData[-1].Seats
        RoomData.pop(-1)
    else:
        while AllotedSeats < RequiredSeats:
            for i in RoomData:
                if RequiredSeats - AllotedSeats >= (i.Seats * 0.5):
                    RequiredRooms.append(i)
                    CurrentRoomSeats = i.Seats
                    RoomData.remove(i)
                    AllotedSeats += CurrentRoomSeats
                else:
                    if RequiredSeats - AllotedSeats < 15:
                        tempFlag = eval(input("\nThenumber of students left is less than 50% of the capacity of the smallest room available. Do you want to allot a new room? (1|0):"))
                        if tempFlag == 1:
                            RequiredRooms.append(RoomData[-1])
                            CurrentRoomSeats = RoomData[-1].Seats
                            RoomData.pop(-1)
                            AllotedSeats += CurrentRoomSeats
                            flag = 1
                            break
                        else:
                            if RequiredSeats - AllotedSeats <= 2 * (sum(j.Columns for j in RequiredRooms)):
                                while AllotedSeats < RequiredSeats:
                                    for i in range(len(RequiredRooms)):
                                        RequiredRooms[i].Rows += 1
                                        RequiredRooms[i].Seats += 2 * RequiredRooms[i].Columns
                                        AllotedSeats += 2 * RequiredRooms[i].Columns
                                        if AllotedSeats >= RequiredSeats:
                                            break
                                flag = 1
                                break
                            else:
                                print('\nAn extra room has to be allotted as the students cannot be allotted the existing room.\n')
                                RequiredRooms.append(RoomData[-1])
                                CurrentRoomSeats = RoomData[-1].Seats
                                RoomData.pop(-1)
                                AllotedSeats += CurrentRoomSeats
                                flag = 1
                                break
                    else:
                        continue
            if flag == 1:
                break

# Create seating arrangements for each room
for i in RequiredRooms:
    for row in range(i.Rows):
        i.Seating.append([])
        for col in range(i.Columns):
            i.Seating[row].append([])
            for desk in range(2):
                i.Seating[row][col].append([])
                i.Seating[row][col][desk] = 0

counter = 0
prn = [k for k in Student_Sub_Dict.keys()]

# Allocate students to seats in each room
for i in RequiredRooms:
    if counter < len(prn):
        if i.SeatsFilled <= i.Seats / 2:
            for col in range(i.Columns):
                for row in range(i.Rows):
                    if not bool(i.Seating[row][col][0]) and counter < len(prn):
                        i.Seating[row][col][0] = prn[counter]
                        i.SeatsFilled += 1
                        counter += 1
                    else:
                        continue
        else:
            continue
    else:
        break

for i in RequiredRooms:
    if counter < len(prn):
        if i.SeatsFilled < i.Seats:
            for col in range(i.Columns):
                for row in range(i.Rows):
                    if not bool(i.Seating[row][col][1]) and counter < len(prn):
                        i.Seating[row][col][1] = prn[counter]
                        i.SeatsFilled += 1
                        counter += 1
                    else:
                        continue
        else:
            continue
    else:
        break

def process_2d_array(input_2d_array, lookup_dict):
    """
    Processes a 2D array and counts the occurrences of values in a lookup dictionary.

    Args:
        input_2d_array (list): A 2D array containing values to be counted.
        lookup_dict (dict): A dictionary used to look up values and their corresponding counts.

    Returns:
        list: A list containing the result dictionary and the total count of values found.
    """
    result_dict = {}
    totalCount = 0

    for row in input_2d_array:
        for column in row:
            for value in column:
                # Look up the corresponding value in the dictionary
                dict_value = lookup_dict.get(value, None)

                if dict_value is not None:
                    # If the value exists in the dictionary, increment its count in the result_dict
                    result_dict[dict_value] = result_dict.get(dict_value, 0) + 1
                    totalCount += 1

    return [result_dict, totalCount]

RoomContents = {}
TeachersRequired = 0
RequiredTeachers = []
TeacherbyDept = {}

# Get the list of teachers from the database
DB.execute('SELECT teacher_id, teacher_name, department, number_of_duties FROM teachers.teacher_list ORDER BY number_of_duties DESC;')
Teachers = DB.fetchall()

# Calculate the room contents and required teachers for each room
for i in RequiredRooms:
    RoomContents[i] = process_2d_array(i.Seating, Student_Sub_Dict)
    studentCount = RoomContents[i][1]
    teacherCount = 1
    studentCount -= 30
    while studentCount >= 13:
        teacherCount += 1
        studentCount -= 30
    RoomContents[i].append(teacherCount)
    TeachersRequired += teacherCount

# Allocate teachers to rooms based on the number of teachers required
for _ in range(TeachersRequired):
    flag = 1
    while flag:
        index = random.randint(0, len(Teachers) - 1)
        if Teachers[index] not in RequiredTeachers:
            dict_value = Teachers[index][2]
            TeacherbyDept[dict_value] = TeacherbyDept.get(dict_value, 0)
            if TeacherbyDept[dict_value] > 3:
                continue
            else:
                TeacherbyDept[dict_value] += 1
                RequiredTeachers.append({Teachers[index][0]: Teachers[index][1]})
                DB.execute('UPDATE teachers.teacher_list SET number_of_duties=%s WHERE teacher_id = %s;', (Teachers[index][3] + 1, Teachers[index][0]))
                # DBCon.CON.commit()
                flag = 0
        else:
            continue

# Print the allocation details
print('\nSeating Requirement: ', RequiredSeats)
print('\nSeating Arrranged: ', AllotedSeats)
print('\nHalls Alloted: ', [(i.Name, i.Seats) for i in RequiredRooms])
print('\nFaculty Requirement: ', TeachersRequired)
print('\nFaculty Alloted: ', RequiredTeachers)
print('\nNumber of Faculty Alloted by Department: ', TeacherbyDept, '\n')
print('### Allocation Data by Halls ###\n')

# Print the seating arrangement for each room
for i in RequiredRooms:
    count = RoomContents[i][2]
    while count > 0:
        RoomContents[i].append(RequiredTeachers.pop())
        count -= 1
    print('Room Name: ', i.Name, end='\n\n')
    print('Subjects Present: ', RoomContents[i][0], end='\n\n')
    print('Students Present: ', RoomContents[i][1], end='\n\n')
    print('Faculty Requirement: ', RoomContents[i][2], end='\n\n')
    print('Faculty Present: ', RoomContents[i][3:], end='\n\n')
    for row in range(i.Rows):
        for col in range(i.Columns):
            for seat in range(2):
                if i.Seating[row][col][seat] != 0:
                    print(i.Seating[row][col][seat], Student_Sub_Dict[i.Seating[row][col][seat]], sep=',', end=' ')
                else:
                    print(i.Seating[row][col][seat], 'None', end=' ')
            print('|', end='')
        print('\t')
    print('\n')
