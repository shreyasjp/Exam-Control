import DBCon

# Connect to the database
DB = DBCon.DB

class RoomInfo:
    def __init__(self, name, seats, columns, rows):
        self.name = name
        self.seats = seats
        self.columns = columns
        self.rows = rows
        self.seating = []
        self.seats_filled = 0
    
    def is_filled(self):
        return self.seats_filled >= 2*(self.columns * self.rows)
    
    def seating_layout(self):
        # Create seating arrangements for each room
        for row in range(self.rows):
            self.seating.append([])
            for col in range(self.columns):
                self.seating[row].append([])
                for desk in range(2):
                    self.seating[row][col].append([])
                    self.seating[row][col][desk] = 0

# Get all results  from a query
def get_all_data(query):
    DB.execute(query)
    return DB.fetchall()

def fetch_room_data():
    rooms = [
    RoomInfo(i[0], i[1], i[2], i[3])
    for i in get_all_data(
        'SELECT rooms.room_name, room_classes.seats, room_classes.columns, room_classes.rows FROM rooms JOIN room_classes ON rooms.room_class_id = room_classes.room_class_id ORDER BY room_classes.seats DESC;'
    )
    ]
    max_students = sum(i.seats for i in rooms)
    max_desks = sum(i.rows*i.columns for i in rooms)

    return rooms, max_students, max_desks

def room_selection(total_students, total_pairs, addNewRoomController=False):
    rooms, max_seats, max_desks = fetch_room_data()
    required_rooms = []
    desks_alloted = 0
    seats_alloted = 0
    if total_students > max_seats:
        return False
    if total_pairs <= 15:
        required_rooms.append(rooms.pop(-1))
        return required_rooms
    if total_pairs > max_desks:
        while total_students > seats_alloted: 
            for room in rooms:
                for i in range(10, 4, -1):
                    i /= 10
                    if total_students - seats_alloted >= ((room.seats) * i):
                        required_rooms.append(room)
                        seats_alloted += room.seats
                        if total_students <= seats_alloted:
                            return required_rooms
                        break
                continue
            if addNewRoomController or total_students - seats_alloted >= (sum(j.columns*2 if j.seats > 30 else 0 for j in required_rooms)):
            # if addNewRoomController or total_students - seats_alloted >= (sum(j.columns*2 for j in required_rooms)):
                required_rooms.append(room.pop(-1))
                return required_rooms
            for room in required_rooms:
                room.rows += 1
                room.seats += 2 * room.columns
                seats_alloted += room.seats
                if total_students <= seats_alloted:
                    return required_rooms
                continue
    while total_pairs > desks_alloted:
        for room in rooms:
            for i in range(10, 4, -1):
                i /= 10
                if total_pairs - desks_alloted >= ((room.rows*room.columns) * i):
                    required_rooms.append(room)
                    desks_alloted += room.rows*room.columns
                    if total_pairs <= desks_alloted:
                        return required_rooms
                    break
            continue
        if addNewRoomController or total_pairs - desks_alloted >= (sum(j.columns if j.seats > 30 else 0 for j in required_rooms)):
        # if addNewRoomController or total_pairs - desks_alloted >= (sum(j.columns for j in required_rooms)):
            required_rooms.append(rooms.pop(-1))
            return required_rooms
        for room in required_rooms:
            room.rows += 1
            room.seats += 2 * room.columns
            desks_alloted += room.columns
            if total_pairs <= desks_alloted:
                return required_rooms
            continue

def split_and_extract_values(lst):
    first_list = []
    second_list = []
    for pair in lst:
        if None in pair:  # Check if either value is None
            break  # Stop when encountering None
        first_list.append(pair)
    second_list = [pair[0] for pair in lst[len(first_list):] if pair[0] is not None]
    return first_list + second_list


def allocation(required_rooms, students_split):
    counter = 0
    while students_split != []:
        for room in required_rooms:
            for i in range(room.columns):
                for j in range(room.rows):
                    if counter < len(students_split):
                        if type(students_split[counter]) == list:
                                room.seating[j][i] = students_split[counter]
                                counter += 1
                        else:
                            room.seating[j][i][0] = students_split[counter]
                            counter += 1
                    else:
                        break
                else:
                    continue
                break
            else:
                continue
            break
        if counter >= len(students_split):
            break
        for room in required_rooms:
            for i in range(room.columns):
                for j in range(room.rows):
                    if counter < len(students_split):
                        if room.seating[j][i][1] == 0:
                            room.seating[j][i][1] = students_split[counter]
                            counter += 1
                        else:
                            continue
                    else:
                        break
                else:
                    continue
                break
            else:
                continue
            break
        break

def generate_lists_from_tuple(total_numbers, num_nested_arrays):
    nested_arrays = []
    numbers_per_array = total_numbers // num_nested_arrays
    remainder = total_numbers % num_nested_arrays
    index = 0
    for _ in range(num_nested_arrays):
        nested_array = []
        for _ in range(numbers_per_array):
            nested_array.append(index + 1)
            index += 1
        if remainder > 0:
            nested_array.append(index + 1)
            index += 1
            remainder -= 1
        elif (len(nested_array) ==1):
            nested_array.append(None)
        nested_arrays.append(nested_array if nested_array else [None])
    return nested_arrays

a,b = 511, 266
required_rooms = room_selection(a, b)
for room in required_rooms:
    room.seating_layout()
allocation(required_rooms, split_and_extract_values(generate_lists_from_tuple(a,b)))

