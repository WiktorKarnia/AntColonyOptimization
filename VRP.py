import json
import random
import math
import matplotlib.pyplot as plt

num_ants = 5  # Number of vehicles
capacity = 1000  # Capacity of each vehicle

def check_if_doable(cities_data, capacity, num_ants): #Check if all cities can be visited with cars capacity
    total_demand = 0
    for city in cities_data.values():
        total_demand += city['demand']
    return total_demand <= capacity*num_ants


def calculate_distance(coords1, coords2): #Calculate distance between two points on earth
    lat1, lon1 = math.radians(coords1[0]), math.radians(coords1[1])
    lat2, lon2 = math.radians(coords2[0]), math.radians(coords2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = 6371 * c  #Earth circumference
    return distance

#Funkcja obliczająca atrakcyjność przejścia do kolejnego miasta (not sure about this one tbh)
def calculate_attractiveness(city1, city2):
    distance = calculate_distance(city1['coordinates'], city2['coordinates'])
    attractiveness = 1 / (distance + 0.1)
    return attractiveness

#Ant colony optimalization algorithm
def ant_colony_optimization(cities_data, num_ants, capacity):
    city_count = len(cities_data)
    pheromones = {city: [1 for _ in range(len(cities_data))] for city in cities_data}
    evaporation_rate = 0.1  # Współczynnik parowania feromonów
    pheromone_increase = 1  # Wartość wzrostu feromonów dla wybranych tras

    start_city = "Kraków"  # Always start from Krakow
    iterations_paths = []
    all_distances = []
    sum_all_distances = []
    all_paths = [[] for _ in range(num_ants)]  # Paths for each vehicle
    visited_cities = set()  # All visited cities
    
    for _ in range(100):  # Number of iterations
        visited_cities.clear()  # Clear visited cities before each iteration
        for ant in range(num_ants):
            current_city = start_city
            path = [current_city]
            current_capacity = capacity - cities_data[current_city]['demand']
            visited_cities.add(current_city)  # Add start city to visited
            
            while len(visited_cities) < len(cities_data):
                probabilities = []
                for city in cities_data:
                    if city != start_city and city not in path and city not in visited_cities:
                        pheromone = pheromones[current_city][list(cities_data.keys()).index(city)]
                        attractiveness = calculate_attractiveness(cities_data[current_city], cities_data[city])
                        probabilities.append((city, pheromone * attractiveness))

                total = sum(prob[1] for prob in probabilities)
                probabilities = [(city, prob / total) for city, prob in probabilities]

                next_city = random.choices([prob[0] for prob in probabilities], [prob[1] for prob in probabilities])[0]


                if current_capacity - cities_data[next_city]['demand'] >= 0:
                    current_city = next_city
                    path.append(current_city)
                    current_capacity -= cities_data[current_city]['demand']
                    visited_cities.add(next_city)  # Add visited city
                    if len(visited_cities) == city_count:
                        path.append(start_city)  # Add Krakow at the end when vehicle capacity exceeded
                        break
                else:
                    available_cities = [city for city in cities_data if city != start_city and city not in path and city not in visited_cities]
                    other_cities = [city for city in available_cities if current_capacity - cities_data[city]['demand'] >= 0]
                    
                    if other_cities:
                        next_city = random.choice(other_cities)
                        current_city = next_city
                        path.append(current_city)
                        current_capacity -= cities_data[current_city]['demand']
                        visited_cities.add(next_city)
                        if len(visited_cities) == city_count:
                            path.append(start_city)
                            break
                    else:
                        path.append(start_city)
                        break
            
            all_paths[ant] = path.copy()
            
        # Update pheromones
        for city in cities_data:
            for i in range(len(cities_data)):
                pheromones[city][i] *= (1 - evaporation_rate)
                # print(pheromones)

        for path in all_paths:
            path_distance = 0
            for i in range(len(path) - 1):
                city_A = path[i]
                city_B = path[i + 1]
                city_A_index = list(cities_data.keys()).index(city_A)
                city_B_index = list(cities_data.keys()).index(city_B)
                city_A_coords = cities_data[city_A]['coordinates']
                city_B_coords = cities_data[city_B]['coordinates']
                path_distance += calculate_distance(city_A_coords, city_B_coords)

                # Update pheromones for both directions
                pheromones[city_A][city_B_index] += pheromone_increase / path_distance
                pheromones[city_B][city_A_index] += pheromone_increase / path_distance
        
        distances_for_iteration = []
        iterations_paths.append(all_paths)
        
        for path in all_paths:
            distance = 0
            for i in range(len(path) - 1):
                distance += calculate_distance(cities_data[path[i]]['coordinates'], cities_data[path[i + 1]]['coordinates'])
            distances_for_iteration.append(distance)
        all_distances.append(distances_for_iteration)

    for distance in all_distances:
        sum_all_distances.append(sum(distance))
    best_route_distance_total = min(sum_all_distances)
    best_route_index = sum_all_distances.index(best_route_distance_total)
    best_route_distances = all_distances[best_route_index]
    best_route = iterations_paths[best_route_index]
    
    return iterations_paths, all_distances, sum_all_distances, best_route, best_route_distances, best_route_distance_total


def print_best_paths(best_routes, total_distances, cities_data, total_distance):
    for i, route in enumerate(best_routes):
        if i < len(total_distances):
            distance = total_distances[i]
            print(f"Najlepsza trasa dla samochodu {i + 1}: {route}")
            print(f"Długość trasy: {distance:.2f} km")
            print(f"Łączne zapotrzebowanie: {sum(cities_data[city]['demand'] for city in route)}")
            print("\n")
    print(f"Łączna długość trasy: {total_distance:.2f} km")
    print("\n")

def save_all_paths(cities_data, iterations_paths, all_distances, sum_all_distances):
    routes_data = []
    
    # Store the iterations' routes
    for i, paths in enumerate(iterations_paths):
        iteration_data = {
            f"Iteration_{i + 1}": {
                "FullDistance": f"{round(sum_all_distances[i], 2)} km",
                "Routes": []
            }
        }
        for path_index, path in enumerate(paths):
            distance = round(all_distances[i][path_index], 2)
            route_data = {
                "route": path,
                "distance": f"{distance} km",
                "demand": f"{sum(cities_data[city]['demand'] for city in path)}"
            }
            iteration_data[f"Iteration_{i + 1}"]["Routes"].append(route_data)
        routes_data.append(iteration_data)

    with open('all_routes.json', 'w', encoding='utf-8') as file:
        json.dump(routes_data, file, ensure_ascii=False, indent=2)

def save_best_path(cities_data, best_route, best_route_distances, best_route_distance_total):
    best_routes_data = []
    
    # Store the best route
    best_route_data = {
        "BestRoute": {
            "FullDistance": f"{round(best_route_distance_total, 2)} km",
            "Routes": []
        }
    }
    for path_index, path in enumerate(best_route):
        distance = round(best_route_distances[path_index], 2)
        route_data = {
            "route": path,
            "distance": f"{distance} km",
            "demand": f"{sum(cities_data[city]['demand'] for city in path)}"
        }
        best_route_data["BestRoute"]["Routes"].append(route_data)
    best_routes_data.append(best_route_data)

    with open('best_route.json', 'w', encoding='utf-8') as file:
        json.dump(best_routes_data, file, ensure_ascii=False, indent=2)
        
def draw_map(cities_data, paths):
    # Wyciągnij współrzędne miast
    coordinates = {city: data['coordinates'] for city, data in cities_data.items()}

    # Utwórz wykres
    plt.figure(figsize=(10, 8))

    # Dodaj punkty reprezentujące miasta
    for city, coord in coordinates.items():
        plt.plot(coord[1], coord[0], 'o', markersize=8)
        plt.text(coord[1], coord[0], city, fontsize=9)

    # Rysuj linie reprezentujące trasy
    for path in paths:
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF)) 
        for i in range(len(path) - 1):
            city1 = path[i]
            city2 = path[i + 1]
            coord1 = coordinates[city1]
            coord2 = coordinates[city2]
            plt.plot([coord1[1], coord2[1]], [coord1[0], coord2[0]], '-', color=color)

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Map of Cities and Routes')
    plt.grid(True)
    plt.savefig(f'path{random.randint(1000, 9999)}.png')
    plt.show()

# Load cities' data from the JSON file
with open('cities.json', 'r', encoding='utf-8') as file:
    cities_data = json.load(file)
    
if not check_if_doable(cities_data, capacity, num_ants):
    print("Error: Vehicle capacity cannot fulfill the demands of all cities.")
else:

    iterations_paths, all_distances, sum_all_distances, best_route, best_route_distances, best_route_distance_total = ant_colony_optimization(cities_data, num_ants, capacity)

    print_best_paths(best_route, best_route_distances, cities_data, best_route_distance_total)
    save_all_paths(cities_data,iterations_paths, all_distances, sum_all_distances)
    save_best_path(cities_data, best_route, best_route_distances, best_route_distance_total)
    draw_map(cities_data, best_route)

