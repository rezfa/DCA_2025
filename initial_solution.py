import copy

def find_closest_customer(current_location, unvisited_customers, inputs):
    closest_customer = min(unvisited_customers, key=lambda c: inputs.distance_matrix[current_location][c])
    return closest_customer

def find_nearest_charger(current_location, inputs, visited_charging_since_last_customer):
    charger_indices = list(inputs.chargers.keys())  # Get charger indices
    charger_indices.append(0)  # Include the depot as a charging option

    # Exclude recently visited charging stations to avoid loops
    filtered_chargers = [c for c in charger_indices if c not in visited_charging_since_last_customer]

    # If all chargers are excluded, reset the history to allow more options
    if not filtered_chargers:
        filtered_chargers = charger_indices  

    nearest_charger = min(filtered_chargers, key=lambda c: inputs.distance_matrix[current_location][c])
    
    return nearest_charger

def initial_solution(inputs, vehicles):
    """Constructs an initial feasible solution for the problem, tracking time at each node and calculating objective function."""
    unvisited_customers = list(inputs.customers.keys())
    
    for vehicle in vehicles:
        current_location = 0
        trip = 0 # Start with the first trip
        time = 0  # Initialize time tracking
        battery_level = vehicles[vehicle].initial_battery
        visited_charging_since_last_customer = [0]
        
        while unvisited_customers:
            feasible_customers = [c for c in unvisited_customers if vehicles[vehicle].capacities[trip] + inputs.customers[c][5] <= inputs.max_vehicle_volume]
            
            if not feasible_customers:
                # If no customers can be added due to capacity, check depot return condition
                driving_distance = inputs.distance_matrix[current_location][0]
                time += driving_distance / inputs.speed 
                battery_level -= driving_distance * inputs.discharge_rate
                vehicles[vehicle].lengths[trip] += driving_distance
                if time <= 0.9 * inputs.depot[3]:
                    vehicles[vehicle].routes.append([0,0])
                    vehicles[vehicle].charging_quantity.append([0,0])
                    vehicles[vehicle].capacities.append(0)
                    vehicles[vehicle].lengths.append(0)
                    trip += 1
                    current_location = 0 
                    visited_charging_since_last_customer.append(0)
                    continue  # Go back to the start of the while loop for the current vehicle
                break # Exit the loop for this vehicle and move to the next vehicle
            
            # Find the closest feasible customer
            closest_customer = find_closest_customer(current_location, feasible_customers, inputs)
            driving_distance = inputs.distance_matrix[current_location][closest_customer]
            remaining_battery = battery_level - driving_distance * inputs.discharge_rate
            
            if remaining_battery > 0:
                # Check if after adding the customer, the vehicle can reach a charging station or the depot
                nearest_charger = find_nearest_charger(current_location, inputs, visited_charging_since_last_customer)
                distance_to_charger = inputs.distance_matrix[closest_customer][nearest_charger]
                distance_to_depot = inputs.distance_matrix[closest_customer][0]
                
                if remaining_battery - min(distance_to_charger, distance_to_depot) * inputs.discharge_rate > 0:
                    # Insert the customer in the last position of the current trip
                    vehicles[vehicle].routes[trip].insert(len(vehicles[vehicle].routes[trip])-1, closest_customer)
                    vehicles[vehicle].charging_quantity[trip].insert(len(vehicles[vehicle].routes[trip])-1, 0)
                    vehicles[vehicle].lengths[trip] += driving_distance
                    time += driving_distance / inputs.speed + inputs.customers[closest_customer][3]
                    unvisited_customers.remove(closest_customer)
                    battery_level = remaining_battery
                    vehicles[vehicle].capacities[trip] += inputs.customers[closest_customer][5]
                    current_location = closest_customer
                    visited_charging_since_last_customer = []
                else:
                    # Need to go to a charging station first
                    if nearest_charger != 0:
                        vehicles[vehicle].routes[trip].insert(len(vehicles[vehicle].routes[trip])-1, nearest_charger)
                        charging_quantity = inputs.max_battery_capacity - (battery_level - inputs.distance_matrix[current_location][nearest_charger] * inputs.discharge_rate)
                        vehicles[vehicle].charging_quantity[trip].insert(len(vehicles[vehicle].charging_quantity[trip])-1, charging_quantity)
                        time += inputs.distance_matrix[current_location][nearest_charger] / inputs.speed + charging_quantity / inputs.recharge_rate
                        battery_level = inputs.max_battery_capacity
                        current_location = nearest_charger
                        visited_charging_since_last_customer.append(nearest_charger)
                        vehicles[vehicle].lengths[trip] += distance_to_charger
                    else:
                        time += inputs.distance_matrix[current_location][nearest_charger]
                        battery_level -= inputs.distance_matrix[current_location][nearest_charger] * inputs.discharge_rate
                        vehicles[vehicle].lengths[trip] += distance_to_depot
                        if time <= 0.9 * inputs.depot[3]:
                            vehicles[vehicle].routes.append([0,0])
                            vehicles[vehicle].charging_quantity.append([0,0])
                            charging_quantity = inputs.max_battery_capacity - (battery_level - inputs.distance_matrix[current_location][nearest_charger] * inputs.discharge_rate)
                            vehicles[vehicle].charging_quantity[trip][-1] = charging_quantity
                            battery_level = inputs.max_battery_capacity
                            vehicles[vehicle].capacities.append(0)
                            trip += 1
                            current_location = 0
                            visited_charging_since_last_customer.append(0)
                            vehicles[vehicle].lengths.append(0)
                            continue  # Go back to the start of the while loop for the current vehicle
                        break # Exit the loop for this vehicle and move to the next vehicle
            else:
                # Not enough battery to reach the customer, go to the nearest charging station first
                nearest_charger = find_nearest_charger(current_location, inputs, visited_charging_since_last_customer)
                distance_to_charger = inputs.distance_matrix[current_location][nearest_charger]
                if battery_level - distance_to_charger * inputs.discharge_rate > 0:
                    if nearest_charger != 0:
                        vehicles[vehicle].routes[trip].insert(len(vehicles[vehicle].routes[trip])-1, nearest_charger)
                        charging_quantity = inputs.max_battery_capacity - (battery_level - inputs.distance_matrix[current_location][nearest_charger] * inputs.discharge_rate)
                        vehicles[vehicle].charging_quantity[trip].insert(len(vehicles[vehicle].charging_quantity[trip])-1, charging_quantity)
                        time += inputs.distance_matrix[current_location][nearest_charger] / inputs.speed + charging_quantity / inputs.recharge_rate
                        battery_level = inputs.max_battery_capacity
                        current_location = nearest_charger
                        visited_charging_since_last_customer.append(nearest_charger)
                        vehicles[vehicle].lengths[trip] += distance_to_charger
                    else:
                        time += inputs.distance_matrix[current_location][nearest_charger]
                        battery_level -= distance_to_charger * inputs.discharge_rate
                        vehicles[vehicle].lengths[trip] += distance_to_charger
                        if time <= 0.9 * inputs.depot[3]:
                            vehicles[vehicle].routes.append([0,0])
                            vehicles[vehicle].charging_quantity.append([0,0])
                            charging_quantity = inputs.max_battery_capacity - (battery_level - inputs.distance_matrix[current_location][nearest_charger] * inputs.discharge_rate)
                            vehicles[vehicle].charging_quantity[trip][-1] = charging_quantity
                            battery_level = inputs.max_battery_capacity
                            vehicles[vehicle].capacities.append(0)
                            trip += 1
                            current_location = 0
                            visited_charging_since_last_customer.append(0)
                            vehicles[vehicle].lengths.append(0)
                            continue  # Go back to the start of the while loop for the current vehicle
            
                        break # Exit the loop for this vehicle and move to the next vehicle
                        
                else:
                    if time <= 0.9 * inputs.depot[3]:
                        vehicles[vehicle].routes.append([0,0])
                        vehicles[vehicle].charging_quantity.append([0,0])
                        vehicles[vehicle].capacities.append(0)
                        vehicles[vehicle].lengths.append(0)
                        trip += 1
                        current_location = 0
                        continue  # Go back to the start of the while loop for the current vehicle
                    break # Exit the loop for this vehicle and move to the next vehicle
        
        # Check if it's possible to return to the depot from the last customer
        if not unvisited_customers:
            distance_to_depot = inputs.distance_matrix[current_location][0]
            
            while battery_level - distance_to_depot * inputs.discharge_rate < 0:  # Check if battery is sufficient
                # Not enough battery to reach the depot, go to the nearest charging station
                nearest_charger = find_nearest_charger(current_location, inputs, visited_charging_since_last_customer)
                vehicles[vehicle].routes[trip].insert(len(vehicles[vehicle].routes[trip])-1, nearest_charger)  # Add charging station to the route
                distance_to_charger = inputs.distance_matrix[current_location][nearest_charger] 
                charging_quantity = inputs.max_battery_capacity - (battery_level - distance_to_charger * inputs.discharge_rate)
                vehicles[vehicle].charging_quantity[trip].insert(len(vehicles[vehicle].charging_quantity[trip])-1, charging_quantity)
                vehicles[vehicle].lengths += distance_to_charger
                time += inputs.distance_matrix[current_location][nearest_charger] / inputs.speed + charging_quantity / inputs.recharge_rate
                battery_level = inputs.max_battery_capacity
                current_location = nearest_charger  # Move to the charging station
                visited_charging_since_last_customer.append(nearest_charger)
                # Recalculate the distance to the depot after charging
                distance_to_depot = inputs.distance_matrix[current_location][0]
    
    for vehicle in vehicles:
        vehicles[vehicle].customers = copy.deepcopy(vehicles[vehicle].routes)
    
                    
    return vehicles

