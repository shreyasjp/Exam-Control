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
                if RequiredSeats - AllotedSeats > (i.Seats * 0.5):
                    RequiredRooms.append(i)
                    CurrentRoomSeats = i.Seats
                    RoomData.remove(i)
                    AllotedSeats += CurrentRoomSeats
                else:
                    if 10 <= RequiredSeats - AllotedSeats < 16:
                        if RequiredSeats - AllotedSeats > (i.Seats * 0.25):
                            RequiredRooms.append(i)
                            CurrentRoomSeats = i.Seats
                            RoomData.remove(i)
                            AllotedSeats += CurrentRoomSeats
                    if RequiredRooms and RequiredSeats - AllotedSeats <= 2*(sum(j.Columns for j in RequiredRooms)) and RequiredSeats - AllotedSeats < 10:
                        flag = 1
                        break
                    continue
            if flag == 1:
                break

    print(RequiredSeats, AllotedSeats, dict((i.Name, i.Seats) for i in RequiredRooms))
    RoomsRequired = dict((i.Name, i.Seats) for i in RequiredRooms)

import random
import copy

class RoomInfo:
    def __init__(self, name, seats, columns, rows):
        self.Name = name
        self.Seats = seats
        self.Columns = columns
        self.Rows = rows

# Assuming you already have Student_Sub_Dict, TotalStudentsPerSub, RoomData, RequiredRooms, MaxCapacity, RequiredSeats, AllotedSeats, flag

# Function to create an initial population of chromosomes
def create_initial_population(population_size, rooms):
    population = []
    for _ in range(population_size):
        chromosome = random.sample(rooms, len(rooms))
        population.append(chromosome)
    return population

# Function to calculate the fitness of a chromosome
def calculate_fitness(chromosome):
    allocated_seats = 0
    for room in chromosome:
        allocated_seats += room.Seats
    return allocated_seats

# Function to perform crossover (single-point crossover in this example)
def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:crossover_point] + [room for room in parent2 if room not in parent1[:crossover_point]]
    child2 = parent2[:crossover_point] + [room for room in parent1 if room not in parent2[:crossover_point]]
    return child1, child2

# Function to perform mutation (swap mutation in this example)
def mutate(chromosome):
    mutated_chromosome = copy.deepcopy(chromosome)
    mutation_point1, mutation_point2 = random.sample(range(len(chromosome)), 2)
    mutated_chromosome[mutation_point1], mutated_chromosome[mutation_point2] = (
        mutated_chromosome[mutation_point2],
        mutated_chromosome[mutation_point1],
    )
    return mutated_chromosome

# Function to select parents based on tournament selection
def select_parents(population, tournament_size):
    selected_parents = []
    for _ in range(len(population)):
        tournament = random.sample(population, tournament_size)
        winner = max(tournament, key=calculate_fitness)
        selected_parents.append(winner)
    return selected_parents

# Genetic Algorithm
def genetic_algorithm(population_size, generations, crossover_prob, mutation_prob, tournament_size):
    population = create_initial_population(population_size, RoomData)

    for generation in range(generations):
        parents = select_parents(population, tournament_size)
        offspring = []

        for i in range(0, len(parents), 2):
            parent1, parent2 = parents[i], parents[i + 1]
            if random.random() < crossover_prob:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2

            if random.random() < mutation_prob:
                child1 = mutate(child1)
            if random.random() < mutation_prob:
                child2 = mutate(child2)

            offspring.extend([child1, child2])

        population = offspring

        # Termination condition: If the best solution allocates all students, break the loop
        best_solution = max(population, key=calculate_fitness)
        if calculate_fitness(best_solution) == RequiredSeats:
            break

    best_solution = max(population, key=calculate_fitness)
    return best_solution

# Example usage
best_allocation = genetic_algorithm(
    population_size=50,
    generations=100,
    crossover_prob=0.8,
    mutation_prob=0.2,
    tournament_size=5,
)

# Output
allocated_students = {}
for subject, room in zip(TotalStudentsPerSub, best_allocation):
    allocated_students.setdefault(room.Name, []).append(subject)

print("Allocated Students:")
for room_name, subjects in allocated_students.items():
    print(f"{room_name}: {subjects}")