import json
import random
import math
import matplotlib.pyplot as plt

class ACOSimulator:
    
    def __init__(
            self, 
            cars, 
            car_capacity, 
            cities_data,
            iterations, 
            pheromones,
            evaporation_rate,
            pheromone_increase,
            start_city,
            city_count
        ):
        self.cars = cars
        self.car_capacity = car_capacity
        self.cities_data = cities_data
        self.iterations = iterations
        self.pheromones = pheromones
        self.evaporation_rate = evaporation_rate
        self.pheromone_increase = pheromone_increase
        self.start_city = start_city
        self.city_count = city_count

    def calculate_distance(self, coords1, coords2): #Calculate distance between two points on earth
        lat1, lon1 = math.radians(coords1[0]), math.radians(coords1[1])
        lat2, lon2 = math.radians(coords2[0]), math.radians(coords2[1])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = 6371 * c  #Earth circumference
        return distance
    
    def calculate_attractiveness(self, city1, city2):
        distance = self.calculate_distance(city1['coordinates'], city2['coordinates'])
        attractiveness = 1 / (distance + 0.1)
        return attractiveness
    
    def check_if_city_candidate(self, city, path, visited_cities):
        return True if city != start_city and city not in path and city not in visited_cities else False
    
    def calculate_probability(self, current_city, city, every_city_probability):
        pheromone = pheromones[current_city][list(self.cities_data.keys()).index(city)]
        attractiveness = self.calculate_attractiveness(self.cities_data[current_city], self.cities_data[city])
        every_city_probability.append((city, pheromone * attractiveness))

    def choose_next_city(self, every_city_probability):
        total = sum(probability[1] for probability in every_city_probability)
        every_city_probability = [(city, probability / total) for city, probability in every_city_probability]

        return random.choices([probability[0] for probability in every_city_probability], [probability[1] for probability in every_city_probability])[0]

    def evaporate_phermones(self):
        for city in self.cities_data:
            for pheromone in range(len(self.cities_data)):
                pheromones[city][pheromone] *= (1 - self.evaporation_rate)

    def calculate_path_lenght(self, all_paths):
        for path in all_paths:
            path_lenght = 0
            for city in range(len(path) - 1):
                city_A = path[city]
                city_B = path[city + 1]
                city_A_coords = self.cities_data[city_A]['coordinates']
                city_B_coords = self.cities_data[city_B]['coordinates']
                path_lenght += self.calculate_distance(city_A_coords, city_B_coords)

    def run_simulation(self):
        
        iterations_paths = []
        all_distances = []
        sum_all_distances = []
        all_paths = [[] for car in range(self.cars)]  # Paths for each vehicle
        visited_cities = set() 

        for iteration in range(self.iterations):
            visited_cities.clear()
            for car in range(self.cars):
                current_city = self.start_city
                current_path = [current_city]
                current_capacity = self.car_capacity - self.cities_data[current_city]['demand']
                visited_cities.add(current_city)  # Add start city to visited

                while len(visited_cities) < len(self.cities_data):
                    every_city_probability = []
                    for city in self.cities_data:
                        if self.check_if_city_candidate(city, current_path, visited_cities):
                            self.calculate_probability(current_city, city, every_city_probability)
                
                    next_city = self.choose_next_city(every_city_probability)

                    if current_capacity - self.cities_data[next_city]['demand'] >= 0:
                        current_city = next_city
                        current_path.append(current_city)
                        current_capacity -= self.cities_data[current_city]['demand']
                        visited_cities.add(next_city)  # Add visited city
                        if len(visited_cities) == self.city_count:
                            current_path.append(start_city)  # Add Krakow at the end when vehicle capacity exceeded
                            break
                    else:
                        available_cities = [city for city in self.cities_data if city != start_city and city not in current_path and city not in visited_cities]
                        other_cities = [city for city in available_cities if current_capacity - self.cities_data[city]['demand'] >= 0]
                        
                        if other_cities:
                            next_city = random.choice(other_cities)
                            current_city = next_city
                            current_path.append(current_city)
                            current_capacity -= self.cities_data[current_city]['demand']
                            visited_cities.add(next_city)
                            if len(visited_cities) == self.city_count:
                                current_path.append(start_city)
                                break
                        else:
                            current_path.append(start_city)
                            break
                # Add single car finished path to all car paths    
                all_paths[car] = current_path.copy()

            iterations_paths.append(all_paths)
            self.evaporate_phermones()

            distances_for_iteration = []

            for path in all_paths:
                path_lenght = 0
                for city in range(len(path) - 1):
                    city_A = path[city]
                    city_B = path[city + 1]
                    city_A_coords = self.cities_data[city_A]['coordinates']
                    city_B_coords = self.cities_data[city_B]['coordinates']
                    path_lenght += self.calculate_distance(city_A_coords, city_B_coords)
                for city in range(len(path) - 1):
                    city_A = path[city]
                    city_B = path[city + 1]
                    city_A_index = list(self.cities_data.keys()).index(city_A)
                    city_B_index = list(self.cities_data.keys()).index(city_B)
                        
                    pheromones[city_A][city_B_index] += pheromone_increase / path_lenght
                    pheromones[city_B][city_A_index] += pheromone_increase / path_lenght
                distances_for_iteration.append(path_lenght)

            all_distances.append(distances_for_iteration)

        for distance in all_distances:
            sum_all_distances.append(sum(distance))

        best_route_distance_total = min(sum_all_distances)
        best_route_index = sum_all_distances.index(best_route_distance_total)
        best_route_distances = all_distances[best_route_index]
        best_route = iterations_paths[best_route_index]

        return iterations_paths, all_distances, sum_all_distances, best_route, best_route_distances, best_route_distance_total
        #return iterations_paths

if __name__ == "__main__":

    # cars = 5
    # car_capacity = 1000
    # iterations = 100
    # with open('cities.json', 'r', encoding='utf-8') as file:
    #     cities_data = json.load(file)
    # pheromones = {city: [1 for _ in range(len(cities_data))] for city in cities_data}
    # evaporation_rate = 0.1
    # pheromone_increase = 1
    # start_city = "Kraków"
    # city_count = len(cities_data)

    # simulation = ACOSimulator(
    #         cars, 
    #         car_capacity, 
    #         cities_data, 
    #         iterations, 
    #         pheromones,
    #         evaporation_rate,
    #         pheromone_increase,
    #         start_city,
    #         city_count
    #     )
    # print(simulation.run_simulation())

#---------------------------------------------------------------------

    def check_if_doable(cities_data, capacity, num_ants): #Check if all cities can be visited with cars capacity
        total_demand = 0
        for city in cities_data.values():
            total_demand += city['demand']
        return total_demand <= capacity*num_ants
    
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
    
    cars = 5
    car_capacity = 1000
    iterations = 100
    with open('cities.json', 'r', encoding='utf-8') as file:
        cities_data = json.load(file)
    pheromones = {city: [1 for _ in range(len(cities_data))] for city in cities_data}
    evaporation_rate = 0.1
    pheromone_increase = 1
    start_city = "Kraków"
    city_count = len(cities_data)

    if not check_if_doable(cities_data, car_capacity, cars):
        print("Error: Vehicle capacity cannot fulfill the demands of all cities.")
    else:

        simulation = ACOSimulator(
            cars, 
            car_capacity, 
            cities_data, 
            iterations, 
            pheromones,
            evaporation_rate,
            pheromone_increase,
            start_city,
            city_count
        )

        iterations_paths, all_distances, sum_all_distances, best_route, best_route_distances, best_route_distance_total = simulation.run_simulation()

        print_best_paths(best_route, best_route_distances, cities_data, best_route_distance_total)
        save_all_paths(cities_data,iterations_paths, all_distances, sum_all_distances)
        save_best_path(cities_data, best_route, best_route_distances, best_route_distance_total)
        draw_map(cities_data, best_route)
