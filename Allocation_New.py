import ExamControlFunctions as FN # Defined functions library

import datetime as dt
weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

class SplitArrayByScore:   

    def __init__(self, item_list, item_score_dict):
        self.item_list = item_list
        self.item_score_dict = item_score_dict
        self.array1 = []
        self.array2 = []
        self.bestCombination = self.split_array_by_score()


    def generate_splits(self):
        n = len(self.item_list)
        split_size = n // 2
        combinations = []
        for i in range(2**n):
            bin_str = bin(i)[2:].zfill(n)
            if bin_str.count('1') == split_size:
                combination = ([], [])
                for j, bit in enumerate(bin_str):
                    combination[int(bit)].append(self.item_list[j])
                combinations.append(combination)
        
        return combinations

    def find_best_split(self):
        combinations_list = self.generate_splits()
        best_combination = None
        best_difference = float('inf')
        for split1, split2 in combinations_list:
            sum1 = sum(self.item_score_dict.get(i, 0) for i in split1)
            sum2 = sum(self.item_score_dict.get(i, 0) for i in split2)
            # sum1 = sum(split1)
            # sum2 = sum(split2)
            difference = abs(sum1 - sum2)
            if difference < best_difference:
                best_combination = (split1, split2)
                best_difference = difference

        self.array1 += best_combination[0]
        self.array2 += best_combination[1]

        best_combination = [self.array1, self.array2]
        
        return best_combination
    
    def find_equal_splits(self):
        for i in self.item_list:
            for j in self.item_list:
                if i != j and self.item_score_dict[i] == self.item_score_dict[j]:
                    self.array1.append(i)
                    self.array2.append(j)
                    self.item_list.remove(i)
                    self.item_list.remove(j)
                    break

    def make_array_even(self):
        if len(self.item_list) % 2 != 0:
            self.item_list.append(None)

    def split_array_by_score(self):
        self.find_equal_splits()
        self.make_array_even()

        return self.find_best_split()

def fetch_programme_list(level = 'UG'):
    query1 = f"SELECT DISTINCT(programme) AS programme FROM user_data.students and level = {level}"
    query2 = 'SHOW TABLES FROM students;'
    return [i[0] for i in FN.get_all_data(query2)]

def get_student_list(programme, batch = 2021, level = 'UG'):
    query1 = f"SELECT prn, name FROM exam_cell_data.students WHERE program = {programme} and batch = {batch} and level = {level};"
    return [i[0] for i in FN.get_all_data(query1)]

def get_batches(programme):
    query1 = f"SELECT DISTINCT(batch) AS batch FROM user_data.students WHERE programme = {programme};"
    return [i[0] for i in FN.get_all_data(query1)]

def get_exam_data(examData,paperData):
    paper_students = {}
    paper_students_count = {}

    examData['Day'] = (dt.datetime.strptime(examData['Date'], '%d/%m/%Y').weekday() + 1) % 7
    papers = list(paperData.keys())
    for i in paperData:
        paper_students[i] = []
        for j in i['ProgrammeList']:
            program = j
            batch = i['ProgrammeList'][j]
            paper_students[i] += get_student_list(program, batch, examData['Level'])
        for j in i['AddedStudents']:
            if j not in paper_students:
                paper_students.append(j)
        for j in i['RemovedStudents']:
            if j in paper_students:
                paper_students.remove(j)
        paper_students_count[i] = len(paper_students[i])

a=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
b={'a': 4, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9, 'j': 10}
split = SplitArrayByScore(a[:4], b)
print(split.bestCombination)