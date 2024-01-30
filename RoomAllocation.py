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

RequiredSeats = TotalStudents
AllotedSeats = 0

flag = 0

if RequiredSeats>MaxCapacity:
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

                    """ if 10 <= RequiredSeats - AllotedSeats < 16:
                        if RequiredSeats - AllotedSeats > (i.Seats * 0.25): 
                            RequiredRooms.append(i)
                            CurrentRoomSeats = i.Seats
                            RoomData.remove(i)
                            AllotedSeats += CurrentRoomSeats
                    if RequiredRooms and RequiredSeats - AllotedSeats <= 2*(sum(j.Columns for j in RequiredRooms)) and RequiredSeats - AllotedSeats < 10:
                        flag = 1
                        break """
                    
                    if RequiredSeats - AllotedSeats < 15:
                        # tempFlag = eval(input("\nThenumber of students left is less than 50% of the capacity of the smallest room available. Do you want to allot a new room? (1|0):"))
                        tempFlag = 0
                        if tempFlag == 1:
                            RequiredRooms.append(RoomData[-1])
                            CurrentRoomSeats = RoomData[-1].Seats
                            RoomData.pop(-1)
                            AllotedSeats += CurrentRoomSeats
                            flag =1
                            break
                        else:
                            if RequiredSeats - AllotedSeats <= 2*(sum(j.Columns for j in RequiredRooms)):
                                while AllotedSeats < RequiredSeats:
                                    for i in range (len(RequiredRooms)):
                                        RequiredRooms[i].Rows += 1
                                        RequiredRooms[i].Seats += 2*RequiredRooms[i].Columns
                                        AllotedSeats += 2*RequiredRooms[i].Columns
                                        if AllotedSeats >= RequiredSeats:
                                            break
                                flag = 1
                                break
                            else:
                                print('\nAn exta room has to be alloted as the students cannot be alloted the the existing room.\n')
                                RequiredRooms.append(RoomData[-1])
                                CurrentRoomSeats = RoomData[-1].Seats
                                RoomData.pop(-1)
                                AllotedSeats += CurrentRoomSeats
                                flag =1
                                break
                    else:
                        continue
            if flag == 1:
                break

    print('\n', RequiredSeats, AllotedSeats, dict((i.Name, i.Seats) for i in RequiredRooms))
    # print()
    # RoomsRequired = dict((i.Name, i.Seats) for i in RequiredRooms)

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


for i in RequiredRooms:
    if counter < len(prn):
        if i.SeatsFilled <= i.Seats/2:            
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
    result_dict = {}

    for row in input_2d_array:
        for column in row:
            for value in column:
                # Look up the corresponding value in the dictionary
                dict_value = lookup_dict.get(value, None)

                if dict_value is not None:
                    # If the value exists in the dictionary, increment its count in the result_dict
                    result_dict[dict_value] = result_dict.get(dict_value, 0) + 1

    return result_dict

for i in RequiredRooms:
    print(i.Name)
    print(process_2d_array(i.Seating, Student_Sub_Dict))
    for row in range(i.Rows):
        for col in range(i.Columns):
            for seat in range(2):
                if i.Seating[row][col][seat] != 0:
                    print(i.Seating[row][col][seat], Student_Sub_Dict[i.Seating[row][col][seat]],sep=',', end=' ')
                else:
                    print(i.Seating[row][col][seat], 'None', end=' ')
            print('|', end='')
        print('\t')
    print('\n')
print()