def determine_unloading_completion_time(vehicle,inputs):
    unloading_completion_times = []
    for route in range(len(vehicle.routes)):
        unloading_completion_times.append([])
        time = vehicle.charging_quantity[route][0]
        for loc in range(len(vehicle.routes[route])):
            if vehicle.routes[route][loc] == 0:
                time += inputs.distance_matrix[vehicle.routes[route][loc - 1]][vehicle.routes[route][loc]] / inputs.speed 
                time += vehicle.charging_quantity[route][loc]
            if vehicle.routes[route][loc] in list(inputs.customers.keys()):
                time += inputs.distance_matrix[vehicle.routes[route][loc - 1]][vehicle.routes[route][loc]] / inputs.speed 
                time += inputs.customers[vehicle.routes[route][loc]][3]                
            if vehicle.routes[route][loc] in list(inputs.chargers.keys()):
                time += inputs.distance_matrix[vehicle.routes[route][loc - 1]][vehicle.routes[route][loc]] / inputs.speed 
                time += vehicle.charging_quantity[route][loc]
            if vehicle.routes[route][loc] in list(inputs.lockers.keys()):
                time += inputs.distance_matrix[vehicle.routes[route][loc - 1]][vehicle.routes[route][loc]] / inputs.speed 
                if [vehicle.routes[route][loc]] != [vehicle.routes[route][loc - 1]]:
                    time += inputs.lockers[vehicle.routes[route][loc]][3]     
            unloading_completion_times[route].append(time)
    return unloading_completion_times

def locker_delivery(vehicles,inputs):
    locker_delivery = [0] * inputs.num_customers  # Initialize all customers as locker deliveries (1)

    for vehicle in list(vehicles.keys()):
        for route in range(len(vehicles[vehicle].routes)):# Iterate through each vehicle's list of routes
            for loc in range(len(vehicles[vehicle].routes[route])):
                if vehicles[vehicle].routes[route][loc] in list(inputs.lockers.keys()):
                    customer = vehicles[vehicle].customers[route][loc]
                    locker_delivery[customer - 1] = vehicles[vehicle].routes[route][loc]  # Mark customer as home delivery (0)
    return locker_delivery
            
def evaluate_penalty_costs(vehicle, inputs):
    penalty_cust = 0
    if not vehicle.routes:  # Handle vehicles with no routes
        return 0, 0
    for route in range(len(vehicle.routes)):
        for loc in range(1, len(vehicle.routes[route]) - 1):
            if vehicle.routes[route][loc] in list(inputs.customers.keys()):
               penalty_cust += inputs.cost_per_time_late_customer * max(vehicle.unloading_completion_time[route][loc] - inputs.customers[vehicle.routes[route][loc]][4], 0)
    penalty_depot = inputs.cost_per_time_late_depot * max(vehicle.unloading_completion_time[-1][-1] - inputs.depot[3], 0)
    return penalty_cust, penalty_depot

def evaluate_locker_costs(vehicle,inputs):
    return len(vehicle.visited_parcel_lockers) * inputs.locker_opening_cost

def evaluate_vehicle_deployment_costs(vehicle,inputs):
    return max(len(route) for route in vehicle.routes) * inputs.vehicle_deployment_cost

def evaluate_travel_costs(vehicle, inputs):
    return sum(vehicle.lengths) * inputs.cost_per_distance 

def compute_objective(vehicles):
    penalty_costs_customer = sum(vehicles[vehicle].penalty_costs_customer for vehicle in vehicles.keys())
    penalty_costs_depot = sum(vehicles[vehicle].penalty_costs_depot for vehicle in vehicles.keys())
    locker_costs = sum(vehicles[vehicle].locker_costs for vehicle in vehicles.keys()) 
    vehicle_deployment_costs = sum(vehicles[vehicle].vehicle_deployment_costs for vehicle in vehicles.keys())
    travel_costs = sum(vehicles[vehicle].travel_costs for vehicle in vehicles.keys())
    total_costs = penalty_costs_customer + penalty_costs_depot + locker_costs + vehicle_deployment_costs + travel_costs
    return total_costs

   
   