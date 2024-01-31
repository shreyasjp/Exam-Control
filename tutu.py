class RoomInfo:
    def __init__(self, name, seats, columns, rows):
        self.Name = name
        self.Seats = seats
        self.Columns = columns
        self.Rows = rows
        self.Seating = []
        self.SeatsFilled = 0

import DBCon
DB = DBCon.DB

Student_Sub_Dict = {}
DB.execute('SELECT * FROM test.prn_sub;')
List = DB.fetchall()
Subs = DB.column_names
for j in  range (1, len(Subs)):
    for i in List:
        Student_Sub_Dict[i[j]] = Subs[j]

TotalStudentsPerSub = {}
StudentsperSub = {}

for i in Subs[1:]:
    TotalStudentsPerSub[i] = len([k for k, v in Student_Sub_Dict.items() if v == i])
    StudentsperSub[i] = [k for k, v in Student_Sub_Dict.items() if v == i]

TotalStudents = len(Student_Sub_Dict)

DB.execute('SELECT room_data.rooms.room_name, room_data.room_class_specs.seats, room_data.room_class_specs.columns, room_data.room_class_specs.rows FROM room_data.rooms JOIN room_data.room_class_specs ON room_data.rooms.room_class_id = room_data.room_class_specs.room_class_id;')
RoomData = DB.fetchall()
for i in RoomData:
    RoomData[RoomData.index(i)] = RoomInfo(i[0], i[1], i[2], i[3])

def filter_rooms_by_subject(rooms, students_per_sub):
    filtered_rooms = []
    for room in rooms:
        room_subjects = set()
        for row in range(room.Rows):
            for col in range(room.Columns):
                for desk in range(2):
                    student_prn = room.Seating[row][col][desk]
                    if student_prn in students_per_sub:
                        room_subjects.add(students_per_sub[student_prn])
        if all(subject in room_subjects for subject in students_per_sub.values()):
            filtered_rooms.append(room)
    return filtered_rooms

RequiredRooms = []
MaxCapacity = sum(i.Seats for i in RoomData)

RequiredSeats = TotalStudents
AllotedSeats = 0

flag = 0

if RequiredSeats > MaxCapacity:
    print("Hail Hitler")
else:
    if RequiredSeats < 16:
        RequiredRooms.append(RoomData[-1])
        AllotedSeats += RoomData[-1].Seats
        RoomData.pop(-1)
    else:
        while AllotedSeats < RequiredSeats:
            # Filter rooms based on subject constraints
            current_subject = Subs[1:]
    
            # Filter rooms based on subject constraints
            available_rooms = filter_rooms_by_subject(RoomData, StudentsperSub[current_subject])

            
            for room in available_rooms:
                if RequiredSeats - AllotedSeats >= (room.Seats * 0.5):
                    RequiredRooms.append(room)
                    CurrentRoomSeats = room.Seats
                    RoomData.remove(room)
                    AllotedSeats += CurrentRoomSeats
                else:
                    # Your existing logic for other conditions
                    # ...
                    
                    if RequiredSeats - AllotedSeats < 15:
                        tempFlag = 0  # eval(input("\nThenumber of students left is less than 50% of the capacity of the smallest room available. Do you want to allot a new room? (1|0):"))
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

    print('\n', RequiredSeats, AllotedSeats, dict((i.Name, i.Seats) for i in RequiredRooms))
    print()
    # RoomsRequired = dict((i.Name, i.Seats) for i in RequiredRooms)

# Print or use the RequiredRooms as needed
for i in RequiredRooms:
    for row in range(i.Rows):
        i.Seating.append([])
        for col in range(i.Columns):
            i.Seating[row].append([])
            for desk in range(2):
                i.Seating[row][col].append([])
                i.Seating[row][col][desk] = 0
