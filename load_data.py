import re
import numpy as np


class Inputs:
    def __init__(self, id, num_customers, num_chargers, num_lockers,
                 num_vehicles, speed, max_vehicle_volume, max_battery_capacity, 
                 discharge_rate, recharge_rate, locker_radius, locker_opening_cost, 
                 vehicle_deployment_cost, cost_per_distance, cost_per_time_late_customer, 
                 cost_per_time_late_depot, vehicles, depot, customers, chargers, lockers):
        # Initialize attributes
        self.id = id
        self.num_customers = num_customers
        self.num_chargers = num_chargers
        self.num_lockers = num_lockers
        self.num_vehicles = num_vehicles
        self.speed = speed
        self.max_vehicle_volume = max_vehicle_volume
        self.max_battery_capacity = max_battery_capacity
        self.discharge_rate = discharge_rate
        self.recharge_rate = recharge_rate
        self.locker_radius = locker_radius
        self.locker_opening_cost = locker_opening_cost
        self.vehicle_deployment_cost = vehicle_deployment_cost
        self.cost_per_distance = cost_per_distance
        self.cost_per_time_late_customer = cost_per_time_late_customer
        self.cost_per_time_late_depot = cost_per_time_late_depot
        self.vehicles = vehicles
        self.depot = depot
        self.customers = customers
        self.chargers = chargers
        self.lockers = lockers
        
        # Compute the distance matrix
        self.distance_matrix = self.compute_distance_matrix()

    def compute_distance_matrix(self):
        """Computes the Euclidean distance matrix for all locations, using dictionary keys."""
        all_locations = [self.depot] + list(self.customers.values()) + list(self.chargers.values()) + list(self.lockers.values())
        num_locations = len(all_locations)
    
        distance_matrix = np.zeros((num_locations, num_locations))
    
        for i in range(num_locations):
            for j in range(num_locations):
                if i != j:  # No need to compute distance to itself
                    x1, y1 = all_locations[i][0], all_locations[i][1]  # x and y coordinates of location i
                    x2, y2 = all_locations[j][0], all_locations[j][1]  # x and y coordinates of location j
                    distance_matrix[i][j] = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
        return distance_matrix



def extract_locations(lines, start_index, num_items):
    """Helper function to extract location data (customers, chargers, lockers) from file lines."""
    locations = {}
    for i in range(num_items):
        location_data = list(map(float, re.findall(r'[-+]?[0-9]*\.?[0-9]+', lines[start_index + i])))
        # Ensure that the first element is an integer
        location_data[0] = int(location_data[0])
        # Set the first element as the key
        key = int(location_data[0])
        # Store the rest of the data as the value
        locations[key] = location_data
        
    return locations


def load_instance(file_path):
    with open(file_path, 'r') as file:
        lines = [line for line in file.readlines()]

    # Read general instance parameters
    instance_id = int(lines[0])
    num_customers = int(lines[2])
    num_chargers = int(lines[3])
    num_lockers = int(lines[4])
    num_vehicles = int(lines[5])
    speed = float(lines[6])
    max_vehicle_volume = int(lines[7])
    max_battery_capacity = int(lines[8])
    discharge_rate = float(lines[9])
    recharge_rate = float(lines[10])
    locker_radius = float(lines[11])
    locker_opening_cost = float(lines[12])
    vehicle_deployment_cost = float(lines[13])
    cost_per_distance = float(lines[14])
    cost_per_time_late_customer = float(lines[15])
    cost_per_time_late_depot = float(lines[16])

    # Extract vehicles (vehicle_id, initial_battery)
    vehicle_index = 17
    vehicles = []
    for i in range(num_vehicles):
        vehicle_data = list(map(int, re.findall(r'\d+', lines[vehicle_index + i])))
        # Use vehicle_id as the first element
        vehicles.append([vehicle_data[0], vehicle_data[1]])

    # Extract locations (Depot, Customers, Chargers, Lockers)
    depot_index = vehicle_index + num_vehicles
    depot = list(map(float, re.findall(r'[-+]?[0-9]*\.?[0-9]+', lines[depot_index])))

    customers = extract_locations(lines, depot_index + 1, num_customers)
    chargers = extract_locations(lines, depot_index + num_customers + 1, num_chargers)
    lockers = extract_locations(lines, depot_index + num_customers + num_chargers + 1, num_lockers)

    return Inputs(
        instance_id, num_customers, num_chargers, num_lockers, num_vehicles, speed,
        max_vehicle_volume, max_battery_capacity, discharge_rate, recharge_rate,
        locker_radius, locker_opening_cost, vehicle_deployment_cost,
        cost_per_distance, cost_per_time_late_customer, cost_per_time_late_depot,
        vehicles, depot, customers, chargers, lockers
    )


class Vehicles:
    def __init__(self, vehicle_id, initial_battery):
        self.vehicle_id = vehicle_id  # Unique ID for the vehicle
        self.initial_battery = initial_battery  # Initial battery level
        self.routes = [[0,0]]  # List of trips, each trip is a list of nodes
        self.customers = [] # List of customers served (routes might contains lockers, but here the corresponding customer is stored)
        self.charging_quantity =  [[0,0]] 
        self.costs = [0]  # Cost per trip
        self.lengths = [0]  # Distance per trip
        self.capacities = [0]  # Capacity used per trip
        self.visited_parcel_lockers = [0] # Visited parcel lockers

