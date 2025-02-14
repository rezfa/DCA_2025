import re

class Inputs:
    def __init__(self, id, num_customers, num_chargers, num_lockers,
                num_vehicles, speed, max_vehicle_volume, max_battery_capacity, 
                discharge_rate, recharge_rate,locker_radius, locker_opening_cost, 
                vehicle_deployment_cost,cost_per_distance, cost_per_time_late_customer, 
                cost_per_time_late_depot, vehicles, depot, customers, chargers, lockers):

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


def load_instance(file_path):
    
    with open(file_path, 'r') as file:
        lines = [line for line in file.readlines()]


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
  
    # Vehicles
    vehicles = []
    vehicle_index = 17    #next(i for i, line in enumerate(lines) if '// Vehicle' in line) + 1
    for i in range(num_vehicles):
        vehicle_data = list(map(int, re.findall(r'\d+', lines[vehicle_index + i])))
        vehicles.append([vehicle_data[0], vehicle_data[1]])  # Storing as list within a list
    
    # Depot
    depot_index = vehicle_index + num_vehicles
    depot = list(map(float, re.findall(r'[-+]?[0-9]*\.?[0-9]+', lines[depot_index])))

    # Customers
    customers = []
    customers_index = depot_index + 1
    for i in range(num_customers):
        customer_data = list(map(float, re.findall(r'[-+]?[0-9]*\.?[0-9]+', lines[customers_index + i])))
        customers.append(customer_data)
    
    # Chargers
    chargers = []
    chargers_index = customers_index + num_customers
    for i in range(num_chargers):
        charger_data = list(map(float, re.findall(r'[-+]?[0-9]*\.?[0-9]+', lines[chargers_index + i])))
        chargers.append(charger_data)
    
    # Lockers
    lockers = []
    lockers_index = chargers_index + num_chargers
    for i in range(num_lockers):
        locker_data = list(map(float, re.findall(r'[-+]?[0-9]*\.?[0-9]+', lines[lockers_index + i])))
        lockers.append(locker_data)
    
    return Inputs(num_customers, num_chargers, num_lockers, num_vehicles, speed,
                max_vehicle_volume, max_battery_capacity, discharge_rate, recharge_rate,
                locker_radius, locker_opening_cost, vehicle_deployment_cost,
                cost_per_distance, cost_per_time_late_customer, cost_per_time_late_depot,
                vehicles, depot, customers, chargers, lockers)