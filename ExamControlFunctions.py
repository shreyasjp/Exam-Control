import random
import DBCon
import itertools
import random
from copy import deepcopy

# Connect to the database
DB = DBCon.DB

# Get all results  from a query
def get_all_data(query):
    DB.execute(query)
    return DB.fetchall()

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

def generate_groupings(items, item_values):

    allocation = []
    
    for i in items:
        for j in items:
            if i != j and item_values[i] == item_values[j]:
                allocation.append([i, j])
                items.remove(i)
                items.remove(j)

    best_grouping, best_score = generate_groupings_genetic(items, item_values)

    return allocation+[list(i) for i in best_grouping]

def room_selection(RequiredSeats, max_capacity, rooms):
    print(RequiredSeats)
    flag = 0
    RequiredRooms = []
    AllotedSeats = 0

    # Allocate rooms based on the number of seats required
    if RequiredSeats > max_capacity/2:
        print("The number of students listed cannot be accomodated in the available rooms.")
    elif RequiredSeats < 7:
        RequiredRooms.append(rooms[-1])
        AllotedSeats += rooms[-1].columns*rooms[-1].rows
        rooms.pop(-1)
    else:
        while AllotedSeats <= RequiredSeats:
            for i in rooms:
                if RequiredSeats - AllotedSeats >= ((i.rows*i.columns) * 0.5):
                    RequiredRooms.append(i)
                    CurrentRoomSeats = i.columns*i.rows
                    rooms.remove(i)
                    AllotedSeats += CurrentRoomSeats
                    if AllotedSeats >= RequiredSeats:
                        flag = 1
                        break
                elif RequiredSeats - AllotedSeats < 7.5:
                    tempFlag = eval(input("\nThenumber of students left is less than 50% of the capacity of the smallest room available. Do you want to allot a new room? (1|0):"))
                    flag = 1
                    if tempFlag == 1:
                        RequiredRooms.append(rooms[-1])
                        CurrentRoomSeats = rooms[-1].columns*rooms[-1].rows
                        rooms.pop(-1)
                        AllotedSeats += CurrentRoomSeats                        
                        if AllotedSeats >= RequiredSeats:
                            break
                    elif RequiredSeats - AllotedSeats <= 2 * (sum(j.columns for j in RequiredRooms)):
                        while AllotedSeats < RequiredSeats:
                            for RequiredRoom in RequiredRooms:
                                RequiredRoom.rows += 1
                                RequiredRoom.seats += 2 * RequiredRoom.columns
                                AllotedSeats += RequiredRoom.columns
                                if AllotedSeats >= RequiredSeats:
                                    break
                    else:
                        print('\nAn extra room has to be allotted as the students cannot be allotted the existing room.\n')
                        RequiredRooms.append(rooms[-1])
                        CurrentRoomSeats = rooms[-1].columns*rooms[-1].rows
                        rooms.pop(-1)
                        AllotedSeats += CurrentRoomSeats
                    break
            if flag == 1:
                break

    return RequiredRooms, AllotedSeats

def room_selection2(RequiredSeats, max_capacity, rooms):
    RequiredRooms = []
    AllotedSeats = 0

    # Allocate rooms based on the number of seats required
    if RequiredSeats > max_capacity / 2:
        print("The number of students listed cannot be accommodated in the available rooms.")
    elif RequiredSeats < 7:
        RequiredRooms.append(rooms[-1])
        AllotedSeats += rooms[-1].columns * rooms[-1].rows
        rooms.pop(-1)
    else:
        while AllotedSeats < RequiredSeats:
            for room in rooms:
                room_capacity = room.columns * room.rows
                if RequiredSeats - AllotedSeats >= (room_capacity * 0.5):
                    RequiredRooms.append(room)
                    rooms.remove(room)
                    AllotedSeats += room_capacity
                elif RequiredSeats - AllotedSeats < 7:
                    tempFlag = int(input("\nThe number of students left is less than 50% of the capacity of the smallest room available. Do you want to allot a new room? (1|0): "))
                    if tempFlag == 1:
                        RequiredRooms.append(rooms[-1])
                        AllotedSeats += rooms[-1].columns * rooms[-1].rows
                        rooms.pop(-1)
                    else:
                        print("\nInsufficient seats to allocate.")
                    break
            else:
                print("\nAn extra room has to be allotted as the students cannot be allotted the existing room.")
                RequiredRooms.append(rooms[-1])
                AllotedSeats += rooms[-1].columns * rooms[-1].rows
                rooms.pop(-1)
                break

    return RequiredRooms, AllotedSeats


def process_2d_array(input_2d_array, lookup_dict):
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