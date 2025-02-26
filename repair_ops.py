import copy
from evaluate_solution import determine_unloading_completion_time, evaluate_penalty_costs, evaluate_locker_costs, evaluate_vehicle_deployment_costs, evaluate_travel_costs
from initial_solution import find_nearest_charger

def greedy_insertion_operator(vehicles, uninserted_customers, inputs):
    """
    Greedily inserts uninserted customers into feasible vehicle routes while ensuring 
    capacity and battery feasibility. Charging stops are added if necessary.
    """
    updated_vehicles = {vid: copy.deepcopy(vehicle) for vid, vehicle in vehicles.items()}
    remaining_customers = uninserted_customers.copy()
    
    while remaining_customers:
        customer = remaining_customers.pop(0)
        feasible_insertions = []
        
        for vid, vehicle in updated_vehicles.items():
            for trip_idx, route in enumerate(vehicle.routes):
                for pos in range(1, len(route)):  # Insert between nodes
                    # Capacity Check
                    if vehicle.capacities[trip_idx] + inputs.customers[customer][5] > inputs.max_vehicle_volume:
                        continue
                    
                    prev_loc = route[pos - 1]
                    next_loc = route[pos] if pos < len(route) else None
                    
                    # Battery Check (Consider charging if already at depot or charger)
                    dist_to_customer = inputs.distance_matrix[prev_loc][customer]
                    remaining_battery = vehicle.initial_battery - dist_to_customer * inputs.discharge_rate
                    
                    if remaining_battery < 0:
                        if prev_loc in inputs.chargers or prev_loc == 0:  # If at depot or charger, charge first
                            charge_amount = min(inputs.max_battery_capacity - vehicle.initial_battery, 
                                                dist_to_customer * inputs.discharge_rate)
                            remaining_battery += charge_amount
                            vehicle.charging_quantity[trip_idx][pos - 1] += charge_amount
                        else:
                            charger = find_nearest_charger(prev_loc, inputs, [0])
                            dist_to_charger = inputs.distance_matrix[prev_loc][charger]
                            if vehicle.initial_battery - dist_to_charger * inputs.discharge_rate < 0:
                                continue
                            charge_amount = min(inputs.max_battery_capacity - vehicle.initial_battery, 
                                                dist_to_customer * inputs.discharge_rate)
                            feasible_insertions.append((vid, trip_idx, pos, incremental_cost, charger, charge_amount))
                    
                    # Compute incremental cost
                    cost_without_customer = inputs.distance_matrix[prev_loc][next_loc] if next_loc else 0
                    cost_with_customer = inputs.distance_matrix[prev_loc][customer] + (inputs.distance_matrix[customer][next_loc] if next_loc else 0)
                    incremental_cost = cost_with_customer - cost_without_customer
                    
                    feasible_insertions.append((vid, trip_idx, pos, incremental_cost, None, 0))
        
        if feasible_insertions:
            # Select best insertion based on minimal incremental cost
            best_insertion = min(feasible_insertions, key=lambda x: x[3])
            vid, trip_idx, pos, _, charger, charge_amount = best_insertion
            
            # Apply insertion
            updated_vehicles[vid].routes[trip_idx].insert(pos, customer)
            updated_vehicles[vid].charging_quantity[trip_idx].insert(pos, 0)
            updated_vehicles[vid].capacities[trip_idx] += inputs.customers[customer][5]
            
            if charger:
                updated_vehicles[vid].routes[trip_idx].insert(pos, charger)
                updated_vehicles[vid].charging_quantity[trip_idx].insert(pos, charge_amount)
        else:
            print(f"Customer {customer} could not be inserted into any route.")
            remaining_customers.append(customer)
    
    return updated_vehicles, remaining_customers
