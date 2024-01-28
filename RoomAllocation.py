class RoomInfo:
    def __init__(self, name, seats, columns, rows):
        self.Name = name
        self.Seats = seats
        self.Columns = columns
        self.Rows = rows

import DBCon
DB = DBCon.DB

Student_Sub_Dict = {}
DB.execute('SELECT * FROM test.prn_sub;')
List = DB.fetchall()
Subs = DB.column_names
for j in  range (1, len(Subs)):
    for i in List:
        Student_Sub_Dict[i[j]] = Subs[j]

# [k for k, v in Student_Sub_Dict.items() if v == Subs[3]] # To get all the PRNs of a particular subject
        
TotalStudentsPerSub = {}
for i in Subs[1:]:
    TotalStudentsPerSub[i] = len([k for k, v in Student_Sub_Dict.items() if v == i])

TotalStudents = len(Student_Sub_Dict)

DB.execute('SELECT room_data.rooms.room_name, room_data.room_class_specs.seats, room_data.room_class_specs.columns, room_data.room_class_specs.rows FROM room_data.rooms JOIN room_data.room_class_specs ON room_data.rooms.room_class_id = room_data.room_class_specs.room_class_id;')
RoomData= DB.fetchall()
for i in RoomData:
    RoomData[RoomData.index(i)] = RoomInfo(i[0],i[1], i[2], i[3])

# Find Required rooms by total number of students
    
RequiredRooms = []
MaxCapacity = sum(i.Seats for i in RoomData)

if TotalStudents>MaxCapacity:
    print("Hail Hitler")

RequiredSeats = 182
AllotedSeats = 0
for  i in RoomData:
    if RequiredSeats - AllotedSeats < 2*i.Columns:
        break
    if AllotedSeats + i.Seats < RequiredSeats:
        AllotedSeats += i.Seats
        RequiredRooms.append(i.Name)
    else:
        RequiredRooms.append(i.Name)
        AllotedSeats += i.Seats
        break

print(RequiredSeats, AllotedSeats, RequiredRooms)