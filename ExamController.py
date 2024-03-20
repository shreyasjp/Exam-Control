import openpyxl

# Global Variables
weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
slots = ['Morning','Afternoon']

# Importing defined libraries
import DBCon # Database connectivity
import ExamControlFunctions as FN # Defined functions library

# Importing python libraries
import datetime as dt # datetime library
from itertools import zip_longest # Itertools library
import random # Random number generator
import os # OS for path handling
import pandas as pd # Pandas for data manipulation

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
        return self.seats_filled >= 2(*self.columns * self.rows)
    
    def seating_layout(self):
        # Create seating arrangements for each room
        for row in range(self.rows):
            self.seating.append([])
            for col in range(self.columns):
                self.seating[row].append([])
                for desk in range(2):
                    self.seating[row][col].append([])
                    self.seating[row][col][desk] = 0

programmes = [i[0] for i in FN.get_all_data('SHOW TABLES FROM students;')] # List of all departments in college

print('\n## Add a new Exam ##\n')

exam_name = input('Enter the name of the exam: ') # Input exam name
exam_date = dt.datetime.strptime(input('Enter the date of the exam (DD/MM/YYYY): '), '%d/%m/%Y') # Exam date
exam_day = (exam_date.weekday() + 1) % 7 # Calculating weekday
exam_slot = 1 if input('Enter the slot of the exam (Morning/Afternoon): ') == 'Evening' else 0 # Input exam slot

papers = [] # List of all papers on the day in the slot
paper_programme = {} # List of all programmes by paper
paper_students = {} # List of students for each paper
paper_students_count = {} # Count of students for each paper
paper_student_map = {} # Map of students to papers

print('\n## Add Papers ##')

# Adding papers
while 1:
    paper = input('\nEnter the course code of the paper: ') # Input paper name
    if paper == '': # If no subject is entered
        break
    else:
        papers.append(paper) # Add subject to list
    flag = int(input('\nAdd a new paper (Yes:1/No:0): '))
    if not flag:
        break

# Adding different programmes for each paper
for i in papers:
    paper_programme[i] = []
    paper_students[i] = []
    temp = programmes
    while True:
        print('\nProgrammes List: ', [f"{str(j)} {temp.index(j)}" for j in temp])
        programme_index = int(input(f"\nEnter the index of programme to select students from for {i}: "))
        if programme_index == '':
            break
        loop_temp = temp.pop(programme_index)
        paper_programme[i].append(loop_temp)
        students = [k[0] for k in FN.get_all_data(f'SELECT prn FROM students.{loop_temp}')]
        paper_students[i].extend(students)  # Extending list with students from current programme
        paper_students_count[i] = len(paper_students[i])  # Update count of students for this paper

        # Update paper_student_map
        for student in students:
            paper_student_map[student] = i

        flag_1 = int(input(f"\nAdd students from another programme to {i} (Yes:1/No:0): "))
        if not flag_1:
            while True:
                decision = input(f"\nDo you want to manually add or remove the students from the list for {i} (Add:1/Remove:0/Press Return to continue): ")
                if decision == '':
                    break
                decision = int(decision)
                if decision:
                    while True:
                        prn = input(f"\nEnter the PRN of the student to add to {i} (Press Return to stop): ")
                        if prn == '':
                            break
                        prn = eval(prn)
                        if prn not in paper_students[i]:
                            paper_students[i].append(prn)
                            paper_students_count[i] += 1
                            paper_student_map[prn] = i  # Update paper_student_map
                        else:
                            print("\nPRN already exists in the list")
                elif decision==0:
                    while True:
                        prn = input(f"\nEnter the PRN of the student to remove from {i} (Press Return to stop): ")
                        if prn == '':
                            break
                        prn = eval(prn)
                        if prn in paper_students[i]:
                            paper_students[i].remove(prn)
                            paper_students_count[i] -= 1
                            del paper_student_map[prn]  # Update paper_student_map
                        else:
                            print("\nPRN does not exist in the list")
                else:
                    break
                flag_2 = int(input(f"\nDo you want to manually edit the students list for {i} again (Yes:1/No:0): "))
                if not flag_2:
                    break
            break
    paper_students_count[i] = len(paper_students[i])

total_students = sum(paper_students_count[i] for i in paper_students_count)

rooms = [
    RoomInfo(i[0], i[1], i[2], i[3])
    for i in FN.get_all_data(
        'SELECT room_data.rooms.room_name, room_data.room_class_specs.seats, room_data.room_class_specs.columns, room_data.room_class_specs.rows FROM room_data.rooms JOIN room_data.room_class_specs ON room_data.rooms.room_class_id = room_data.room_class_specs.room_class_id;'
    )
]

max_capacity = sum(i.seats+(i.columns*2) for i in rooms)

student_split = []

if len(papers.copy()) > 1:
    temp = FN.generate_groupings(papers.copy(),paper_students_count)
else:
    temp = [(papers[0],None)]

for paper_pair in temp:
    paper_1_students = paper_students.get(paper_pair[0], [])
    paper_2_students = paper_students.get(paper_pair[1], [])
    
    # Zip the lists together, filling missing values with None
    for student_1, student_2 in zip_longest(paper_1_students, paper_2_students, fillvalue=None):
        student_split.append([student_1, student_2])

seats_required = len(student_split)
rooms_required, seats_alloted = FN.room_selection(len(student_split), max_capacity, rooms)

for room in rooms_required:
    room.seating_layout()

counter = 0
# Assign students to seats
for i in rooms_required:
    for row in range(i.rows):
        for col in range(i.columns):
            for seat in range(2):
                if counter < seats_required:
                    i.seating[row][col][seat] = student_split[counter][seat]
                else:
                    break            
            counter += 1
            if counter >= seats_required:
                break
        if counter >= seats_required:
            break

room_student_distribution = {}

# Print the seating arrangement for each room
for room in rooms_required:
    room_student_distribution[room.name] = {}
    for row in range(room.rows):
        for col in range(room.columns):
            for seat in range(2):
                student = room.seating[row][col][seat]
                if student is not None:
                    paper = paper_student_map.get(student, 'NA')
                    if paper in room_student_distribution[room.name]:
                        room_student_distribution[room.name][paper] += 1
                    else:
                        room_student_distribution[room.name][paper] = 1
    if 'NA' in room_student_distribution[room.name]:
        room_student_distribution[room.name].pop('NA')

teacher_list = FN.get_all_data('SELECT teacher_id, teacher_name, department, number_of_duties FROM teachers.teacher_list ORDER BY number_of_duties DESC;')

room_content = {}
required_teachers = 0
teachers_required = []
teachers_id = []
teacher_dept = {}

# Calculate the room contents and required teachers for each room
for i in rooms_required:
    room_content[i] = FN.process_2d_array(i.seating, paper_student_map)
    studentCount = room_content[i][1]
    teacherCount = 1
    studentCount -= 30
    while studentCount >= 13:
        teacherCount += 1
        studentCount -= 30
    room_content[i].append(teacherCount)
    required_teachers += teacherCount

# Allocate teachers to rooms based on the number of teachers required
for _ in range(required_teachers):
    flag = 1
    while flag:
        index = random.randint(0, len(teacher_list) - 1)
        if teacher_list[index][0] not in teachers_id:
            dict_value = teacher_list[index][2]
            teacher_dept[dict_value] = teacher_dept.get(dict_value, 0)
            if teacher_dept[dict_value] > 3:
                continue
            else:
                teacher_dept[dict_value] += 1
                teachers_required.append({teacher_list[index][0]: teacher_list[index][1]})
                teachers_id.append(teacher_list[index][0])
                DB.execute('UPDATE teachers.teacher_list SET number_of_duties=%s WHERE teacher_id = %s;', (teacher_list[index][3] + 1, teacher_list[index][0]))
                # DBCon.CON.commit()
                flag = 0
        else:
            continue

print()
# Printing the final results
print('## EXAM MANAGEMENT SYSTEM ##')
print('\nExam Name: ', exam_name)
print('\nDate  of Examination:', str(exam_date)[:11]) # Exam Datetime without time
print('\nDay of Examination:', weekdays[exam_day])
print('\nExam Time Slot:', slots[exam_slot])

# Print the allocation details
print('\nSeating Requirement: ', seats_required)
print('\nSeating Arrranged: ', seats_alloted)
print('\nHalls Alloted: ', [(i.name, i.seats) for i in rooms_required])
print('\nFaculty Requirement: ', required_teachers)
print('\nFaculty Alloted: ', teachers_required)
print('\nNumber of Faculty Alloted by Department: ', teacher_dept, '\n')
print('### Allocation Data by Halls ###\n')

# Create a text file for allocation data
file_name = 'AllocationData.txt'
with open(file_name, 'w') as file:
    file.write('Exam Name: ' + exam_name + '\n')
    file.write('Date of Examination: ' + str(exam_date)[:11] + '\n')
    file.write('Day of Examination: ' + weekdays[exam_day] + '\n')
    file.write('Exam Time Slot: ' + slots[exam_slot] + '\n')
    file.write('Seating Requirement: ' + str(seats_required) + '\n')
    file.write('Seating Arranged: ' + str(seats_alloted) + '\n')
    file.write('Halls Alloted: ' + str([(i.name, i.seats) for i in rooms_required]) + '\n')
    file.write('Faculty Requirement: ' + str(required_teachers) + '\n')
    file.write('Faculty Alloted: ' + str(teachers_required) + '\n')
    file.write('Number of Faculty Alloted by Department: ' + str(teacher_dept) + '\n')

allocations = {}
room_paper_distribution  = {}
# Print the seating arrangement for each room
for i in rooms_required:
    room_paper_distribution[i.name] = {}
    count = room_content[i][2]
    while count > 0:
        room_content[i].append(teachers_required.pop())
        count -= 1
    print('Room Name: ', i.name, end='\n\n')
    print('Subjects Present: ', room_content[i][0], end='\n\n')
    print('Students Present: ', room_content[i][1], end='\n\n')
    print('Faculty Requirement: ', room_content[i][2], end='\n\n')
    print('Faculty Present: ', room_content[i][3:], end='\n\n')
    allocations[i.name] = []
    for row in range(i.rows):
        allocations[i.name].append([])
        for col in range(i.columns):
            for seat in range(2):
                allocations[i.name][row].append(i.seating[row][col][seat])
                if i.seating[row][col][seat] != 0:
                    prn_list = room_paper_distribution[i.name].get(paper_student_map.get(i.seating[row][col][seat], 'NA'), [])
                    prn_list.append(i.seating[row][col][seat])
                    room_paper_distribution[i.name][paper_student_map.get(i.seating[row][col][seat], 'NA')] = prn_list
                    print(
                        i.seating[row][col][seat], 
                        paper_student_map.get(i.seating[row][col][seat], 'NA'), 
                        sep=',', 
                        end=' '
                    )
                else:
                    print(i.seating[row][col][seat], 'None', end=' ')
            print('|', end='')
        print('\t')
    print('\n')

# Print the room_paper_distribution
for room, papers in room_paper_distribution.items():
    print(f"Room: {room}")
    for paper, prn_list in papers.items():
        if paper != 'NA':
            print(f"Paper: {paper}")
            if prn_list != None:
                print(f"PRN Range: {prn_list}")
            else:
                print("No PRN data available")
    print('\n')

for i in rooms_required:
    file_name = 'TextFiles/' + i.name + '.txt'
    os.makedirs(os.path.dirname(file_name), exist_ok=True)  # Create directory if it doesn't exist
    with open(file_name, 'w') as file:
        file.write(f"Room Name: {i.name}\n")
        file.write(f"Subjects Present: {room_content[i][0]}\n")
        file.write(f"Students Present: {room_content[i][1]}\n")
        file.write(f"Faculty Requirement: {room_content[i][2]}\n")
        file.write(f"Faculty Present: {room_content[i][3:]}\n")
        file.write('\n')
        for paper, prn_list in room_paper_distribution[i.name].items():
            if paper != 'NA':
                file.write(f"Paper: {paper}\n")
                if prn_list != None:
                    file.write(f"PRN Range: {prn_list}\n")
        file.write('\n')

# Convert data to strings
string_allocations = {key: [[str(item) for item in row] for row in value] for key, value in allocations.items()}

# Create an Excel writer object
with pd.ExcelWriter('exam_allocations.xlsx') as writer:
    # Iterate through each allocation
    for allocation_name, allocation_data in string_allocations.items():
        # Create a DataFrame for the current allocation
        df = pd.DataFrame(allocation_data)
        
        # Write the DataFrame to a new sheet in the Excel workbook
        df.to_excel(writer, sheet_name=allocation_name, index=False)

# Notify the user
print("Excel file 'AllocationsByRoom.xlsx' has been created successfully.")