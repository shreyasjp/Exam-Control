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
        self.Name = name
        self.Seats = seats
        self.Columns = columns
        self.Rows = rows
        self.Seating = []
        self.SeatsFilled = 0

programmes = [i[0] for i in FN.get_all_data('SHOW TABLES FROM students;')] # List of all departments in college

print('\n## Add a new Exam ##\n')

exam_name = input('Enter the name of the exam: ') # Input exam name
exam_date = dt.datetime.strptime(input('Enter the date of the exam (DD-MM-YYYY): '), '%d/%m/%Y') # Exam date
exam_day = (exam_date.weekday() + 1) % 7 # Calculating weekday
exam_slot = 1 if input('Enter the slot of the exam (Morning/Afternoon): ') == 'Evening' else 0 # Input exam slot

papers = [] # List of all papers on the day in the slot
paper_programme = {} # List of all programmes by paper
paper_students = {} # List of students for each paper
paper_students_count = {} # Count of students for each paper

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
        paper_students[i] += ([k[0] for k in FN.get_all_data(f'SELECT prn FROM students.{loop_temp}')])
        flag_1 = int(input(f"\nAdd students from another programme to {i} (Yes:1/No:0): "))
        if not flag_1:
            while True:
                decision = input(f"\nDo you want to manually add or remove the students from the list for {i} (Add:1/Remove:0/Press Return to continue): ")
                decision = int(decision)
                if decision:
                    while True:
                        prn = input(f"\nEnter the PRN of the student to add to {i} (Press Return to stop): ")
                        if prn == '':
                            break
                        prn = eval(prn)
                        if prn not in paper_students[i]:
                            paper_students[i].append(prn)
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
                        else:
                            print("\nPRN does not exist in the list")
                else:
                    break
                flag_2 = int(input(f"\nDo you want to manually edit the students list for {i} again (Yes:1/No:0): "))
                if not flag_2:
                    break
            break
    paper_students_count[i] = len(paper_students[i])

print(exam_name)
print(str(exam_date)[:11]) # Exam Datetime without time
print(weekdays[exam_day])
print(slots[exam_slot])
print(paper_programme)
print(paper_students)
print(paper_students_count)

