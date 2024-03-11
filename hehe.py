# Global Variables
weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
slots = ['Morning','Afternoon']

# Importing defined libraries
import DBCon # Database connectivity
import ExamControlFunctions as FN # Defined functions library

# Importing python libraries
import datetime as dt # datetime library

DB = DBCon.DB # Database connection object

# Room Info custom datatype
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

papers = [] # List of all papers on the day in the slot
paper_students_count = {} # Count of students for each paper

papers = [i[0] for i in FN.get_all_data('SHOW TABLES FROM students;')]

paper_students = {
    paper: [
        i[0] for i in FN.get_all_data(f"SELECT prn FROM students.{paper};")
    ]
    for paper in papers
}

paper_students_count = {
    paper: len([
        i[0] for i in FN.get_all_data(f"SELECT prn FROM students.{paper};")
    ])
    for paper in papers
}

# print(papers)
# print(paper_students)
# print(paper_students_count)

total_students = sum(paper_students_count[i] for i in paper_students_count)
print(total_students)

rooms = [
    RoomInfo(i[0], i[1], i[2], i[3])
    for i in FN.get_all_data(
        'SELECT room_data.rooms.room_name, room_data.room_class_specs.seats, room_data.room_class_specs.columns, room_data.room_class_specs.rows FROM room_data.rooms JOIN room_data.room_class_specs ON room_data.rooms.room_class_id = room_data.room_class_specs.room_class_id;'
    )
]

max_capacity = sum(i.seats+(i.columns*2) for i in rooms)
print(max_capacity)

a=papers.copy()
allocation = []
b={}

for i in a:
    for j in a:
        if i != j and paper_students_count[i] == paper_students_count[j]:
            allocation.append([i, j])
            a.remove(i)
            a.remove(j)

print(allocation)

import itertools
def generate_pairs(items):
    pairs = list(zip(items[::2], items[1::2]))
    if len(items) % 2 != 0:
        pairs.append((items[-1], None))
    return pairs

def calculate_score(group, item_values):
    score = 0
    pair_scores = []
    for pair in group:
        item1, item2 = pair
        try:
            pair_score = abs(item_values[item1] - item_values[item2])
        except KeyError:
            if item1 in item_values:
                pair_score = item_values[item1]
            elif item2 in item_values:
                pair_score = item_values[item2]
            else:
                continue
        score += pair_score
        pair_scores.append((pair, pair_score))
    return score, pair_scores

import random
from copy import deepcopy

def generate_groupings_genetic(items, item_values, population_size=2000, generations=100):
    population = []
    
    # Ensure diversity in initial population
    for _ in range(population_size):
        individual = deepcopy(items)
        random.shuffle(individual)
        population.append(individual)
    
    best_score = float('inf')
    best_grouping = None
    
    for _ in range(generations):
        # Evaluate fitness
        fitness_scores = [calculate_score(generate_pairs(individual), item_values)[0] for individual in population]
        
        # Update best score and grouping
        min_score = min(fitness_scores)
        if min_score < best_score:
            best_score = min_score
            best_grouping = generate_pairs(population[fitness_scores.index(min_score)])
        
        # Selection: Choose top individuals based on fitness
        sorted_population = [x for _, x in sorted(zip(fitness_scores, population))]
        top_individuals = sorted_population[:population_size // 2]
        
        # Crossover: Create new individuals by combining top individuals
        new_population = []
        for _ in range(population_size):
            parent1, parent2 = random.choices(top_individuals, k=2)
            crossover_point = random.randint(0, len(items) - 1)
            child = parent1[:crossover_point] + [gene for gene in parent2 if gene not in parent1[:crossover_point]]
            new_population.append(child)
        
        # Mutation: Introduce random changes to some individuals
        for i in range(population_size):
            if random.random() < 0.1:  # Adjust mutation rate as needed
                mutation_point1, mutation_point2 = random.sample(range(len(items)), 2)
                new_population[i][mutation_point1], new_population[i][mutation_point2] = new_population[i][mutation_point2], new_population[i][mutation_point1]
        
        population = new_population
    
    # Final evaluation and selection
    fitness_scores = [calculate_score(generate_pairs(individual), item_values)[0] for individual in population]
    min_score = min(fitness_scores)
    if min_score < best_score:
        best_grouping = generate_pairs(population[fitness_scores.index(min_score)])
    
    return best_grouping, min_score

# Call the function
a.pop()
best_grouping, best_score = generate_groupings_genetic(a, paper_students_count)

a = allocation+[list(i) for i in best_grouping]
print(a)

side_1 = []
side_2 = []

allocation = []

for paper in [i[0] for i in a]:
    side_1.extend(paper_students[paper])

for paper in [i[1] for i in a]:
    side_2.extend(paper_students[paper])    

while side_1 or side_2:
    if len(side_1) > len(side_2):
        allocation.append([side_1.pop(0), side_2.pop(0) if side_2 else None])
    else:
        allocation.append([side_2.pop(0), side_1.pop(0) if side_1 else None])

# If any elements remain in side_1 or side_2, add them to the left side with None filling in the gaps
while side_1 or side_2:
    if side_1:
        allocation.append([side_1.pop(0), None])
    else:
        allocation.append([side_2.pop(0), None])


RequiredRooms = []
RequiredSeats = len(allocation)
AllotedSeats = 0

flag = 0

# Allocate rooms based on the number of seats required
if RequiredSeats > max_capacity/2:
    print("The number of students listed cannot be accomodated in the available rooms.")
else:
    if RequiredSeats < 16:
        RequiredRooms.append(rooms[-1])
        AllotedSeats += rooms[-1].columns*rooms[-1].rows
        rooms.pop(-1)
    else:
        while AllotedSeats < RequiredSeats:
            for i in rooms:
                if RequiredSeats - AllotedSeats >= (i.seats * 0.5):
                    RequiredRooms.append(i)
                    CurrentRoomSeats = i.columns*i.rows
                    rooms.remove(i)
                    AllotedSeats += CurrentRoomSeats
                else:
                    if RequiredSeats - AllotedSeats < 15:
                        tempFlag = eval(input("\nThenumber of students left is less than 50% of the capacity of the smallest room available. Do you want to allot a new room? (1|0):"))
                        if tempFlag == 1:
                            RequiredRooms.append(rooms[-1])
                            CurrentRoomSeats = rooms[-1].columns*rooms[-1].rows
                            rooms.pop(-1)
                            AllotedSeats += CurrentRoomSeats
                            flag = 1
                            break
                        else:
                            if RequiredSeats - AllotedSeats <= 2 * (sum(j.columns for j in RequiredRooms)):
                                while AllotedSeats < RequiredSeats:
                                    for i in range(len(RequiredRooms)):
                                        RequiredRooms[i].rows += 1
                                        RequiredRooms[i].seats += 2 * RequiredRooms[i].columns
                                        AllotedSeats += 2 * RequiredRooms[i].columns
                                        if AllotedSeats >= RequiredSeats:
                                            break
                                flag = 1
                                break
                            else:
                                print('\nAn extra room has to be allotted as the students cannot be allotted the existing room.\n')
                                RequiredRooms.append(rooms[-1])
                                CurrentRoomSeats = rooms[-1].columns*rooms[-1].rows
                                rooms.pop(-1)
                                AllotedSeats += CurrentRoomSeats
                                flag = 1
                                break
                    else:
                        continue
            if flag == 1:
                break

print([i.name for i in RequiredRooms])

# Create seating arrangements for each room
for i in RequiredRooms:
    for row in range(i.rows):
        i.seating.append([])
        for col in range(i.columns):
            i.seating[row].append([])
            for desk in range(2):
                i.seating[row][col].append([])
                i.seating[row][col][desk] = 0

counter = 0
# Assign students to seats
for i in RequiredRooms:
    for row in range(i.rows):
        for col in range(i.columns):
            for seat in range(2):
                if counter < RequiredSeats:
                    i.seating[row][col][seat] = allocation[counter][seat]
                else:
                    break            
            counter += 1
            if counter >= RequiredSeats:
                break
        if counter >= RequiredSeats:
            break

dict1 = {}
dict2 = {}

# Assign students to subjects
for paper, students in paper_students.items():
    for student in students:
        dict1[student] = paper

# Print the seating arrangement for each room
for room in RequiredRooms:
    print('Room Name: ', room.name, end='\n\n')
    dict2[room.name] = {}
    for row in range(room.rows):
        for col in range(room.columns):
            for seat in range(2):
                student = room.seating[row][col][seat]
                if student is not None:
                    paper = dict1.get(student, 'NA')
                    # Update dict2 with the count of students for each subject in each room
                    if paper in dict2[room.name]:
                        dict2[room.name][paper] += 1
                    else:
                        dict2[room.name][paper] = 1
                    print(student, paper, sep=' # ', end=' ')
                else:
                    print("-", end=' ')  # Print "-" for empty seats
            print('|', end='')
        print('\t')
    print('\n')

# Print the number of students per subject per room
for room, subjects in dict2.items():
    print(f"Room Name: {room}")
    for subject, count in subjects.items():
        print(f"Subject: {subject}, Count: {count}")
    print()
    
RoomContents = {}
TeachersRequired = 0
RequiredTeachers = []
TeacherIDList = []
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
        if Teachers[index][0] not in TeacherIDList:
            dict_value = Teachers[index][2]
            TeacherbyDept[dict_value] = TeacherbyDept.get(dict_value, 0)
            if TeacherbyDept[dict_value] > 3:
                continue
            else:
                TeacherbyDept[dict_value] += 1
                RequiredTeachers.append({Teachers[index][0]: Teachers[index][1]})
                TeacherIDList.append(Teachers[index][0])
                DB.execute('UPDATE teachers.teacher_list SET number_of_duties=%s WHERE teacher_id = %s;', (Teachers[index][3] + 1, Teachers[index][0]))
                # DBCon.CON.commit()
                flag = 0
        else:
            continue