import copy
from evaluate_solution import determine_unloading_completion_time, evaluate_penalty_costs, evaluate_locker_costs, evaluate_vehicle_deployment_costs, evaluate_travel_costs
from initial_solution import find_nearest_charger

def greedy_insertion_operator(vehicles, removed_customers, inputs, original_vehicles):
    """
    Greedily inserts removed customers into vehicle routes, evaluating all feasible positions,
    splitting trips for capacity, ensuring battery feasibility with minimal charging stops,
    preventing customer revisits, and selecting the minimal incremental cost position.

    Parameters:
    - vehicles: Dict of Vehicles objects with customers removed
    - removed_customers: List of customer IDs to reinsert
    - inputs: Inputs object containing problem data
    - original_vehicles: Dict of original Vehicles objects for fallback
    
    Returns:
    - new_vehicles: Updated vehicles with customers reinserted
    - not_inserted: List of customers that could not be inserted (should be empty)
    """
    new_vehicles = {vid: copy.deepcopy(vehicle) for vid, vehicle in vehicles.items()}
    not_inserted = removed_customers.copy()
    
    assigned_customers = set()
    for vehicle in new_vehicles.values():
        for route in vehicle.customers:
            for loc in route:
                if loc in inputs.customers.keys():
                    assigned_customers.add(loc)
    
    while not_inserted:
        customer_to_insert = not_inserted[0]
        if customer_to_insert in assigned_customers:
            not_inserted.remove(customer_to_insert)
            continue
        
        feasible_insertions = []  # List of (vid, trip_idx, pos, additional_stops, new_trip, new_charging, incr_cost)
        
        # Evaluate all possible insertion positions
        for vid, vehicle in new_vehicles.items():
            base_vehicle = copy.deepcopy(vehicle)  # For cost baseline
            base_total_cost = 0
            if base_vehicle.routes:  # Only calculate baseline cost if vehicle has routes
                base_vehicle.unloading_completion_time = determine_unloading_completion_time(base_vehicle, inputs)
                base_penalty_cust, base_penalty_depot = evaluate_penalty_costs(base_vehicle, inputs)
                base_locker_cost = evaluate_locker_costs(base_vehicle, inputs)
                base_deployment_cost = evaluate_vehicle_deployment_costs(base_vehicle, inputs)
                base_travel_cost = evaluate_travel_costs(base_vehicle, inputs)
                base_total_cost = base_penalty_cust + base_penalty_depot + base_locker_cost + base_deployment_cost + base_travel_cost
            
            for trip_idx, route in enumerate(vehicle.routes):
                if len(route) < 2:  # Skip invalid routes
                    continue
                
                # Prevent revisiting the customer in this route
                if customer_to_insert in route:
                    continue
                
                visited_charging_since_last_customer = [0]  # Reset per trip
                current_capacity = vehicle.capacities[trip_idx]
                customer_demand = inputs.customers[customer_to_insert][5]
                
                # Simulate base route with proactive charging
                temp_vehicle = copy.deepcopy(vehicle)
                temp_route = temp_vehicle.routes[trip_idx]
                temp_charging = temp_vehicle.charging_quantity[trip_idx]
                temp_battery = vehicle.initial_battery
                for i in range(1, len(temp_route)):
                    dist = inputs.distance_matrix[temp_route[i-1]][temp_route[i]]
                    next_dist = inputs.distance_matrix[temp_route[i]][temp_route[i+1]] if i + 1 < len(temp_route) else 0
                    temp_battery -= dist * inputs.discharge_rate
                    if (temp_route[i] in inputs.chargers or temp_route[i] == 0) and temp_battery < next_dist * inputs.discharge_rate:
                        charge_amount = min(next_dist * inputs.discharge_rate - temp_battery + 1, inputs.max_battery_capacity - temp_battery)
                        temp_charging[i] = charge_amount
                        temp_battery += charge_amount
                
                for pos in range(1, len(route)):  # Insert between nodes
                    route_copy = route.copy()
                    charging_copy = vehicle.charging_quantity[trip_idx].copy()
                    additional_stops = []  # List of (position, location, charge_amount)
                    new_trip = None
                    new_charging = None
                    temp_battery_at_pos = vehicle.initial_battery
                    
                    # Simulate route up to insertion point
                    for i in range(1, pos):
                        dist = inputs.distance_matrix[route_copy[i-1]][route_copy[i]]
                        next_dist = inputs.distance_matrix[route_copy[i]][route_copy[i+1]] if i + 1 <= pos else dist_to_customer
                        temp_battery_at_pos -= dist * inputs.discharge_rate
                        if temp_battery_at_pos < next_dist * inputs.discharge_rate and (route_copy[i] in inputs.chargers or route_copy[i] == 0):
                            charge_amount = min(next_dist * inputs.discharge_rate - temp_battery_at_pos + 1, inputs.max_battery_capacity - temp_battery_at_pos)
                            charging_copy[i] = charge_amount
                            temp_battery_at_pos += charge_amount
                    
                    if temp_battery_at_pos < 0:
                        continue
                    
                    prev_loc = route_copy[pos - 1]
                    next_loc = route_copy[pos] if pos < len(route_copy) else None
                    
                    # Capacity check and trip splitting
                    needs_split = current_capacity + customer_demand > inputs.max_vehicle_volume
                    if needs_split:
                        dist_to_depot = inputs.distance_matrix[prev_loc][0]
                        if temp_battery_at_pos - dist_to_depot * inputs.discharge_rate >= 0:
                            charge_amount = min(dist_to_depot * inputs.discharge_rate - temp_battery_at_pos + 1 if temp_battery_at_pos < dist_to_depot * inputs.discharge_rate else 0,
                                              inputs.max_battery_capacity - temp_battery_at_pos)
                            if charge_amount > 0:  # Only add mid-route depot if charging is needed
                                additional_stops.append((pos - 1, 0, charge_amount))
                                route_copy = route_copy[:pos] + [0]
                                charging_copy = charging_copy[:pos] + [charge_amount]
                                temp_battery_at_pos = vehicle.initial_battery - dist_to_depot * inputs.discharge_rate + charge_amount
                            new_trip = [0, customer_to_insert, 0]
                            new_charging = [0, 0, 0]
                        else:
                            continue
                    
                    # Battery check to customer
                    dist_to_customer = inputs.distance_matrix[prev_loc][customer_to_insert]
                    battery_after_customer = temp_battery_at_pos - dist_to_customer * inputs.discharge_rate
                    if battery_after_customer < 0:
                        charger = find_nearest_charger(prev_loc, inputs, visited_charging_since_last_customer)
                        dist_to_charger = inputs.distance_matrix[prev_loc][charger]
                        if temp_battery_at_pos < dist_to_charger * inputs.discharge_rate:
                            continue
                        charge_amount = min(dist_to_customer * inputs.discharge_rate - (temp_battery_at_pos - dist_to_charger * inputs.discharge_rate) + 1,
                                          inputs.max_battery_capacity - (temp_battery_at_pos - dist_to_charger * inputs.discharge_rate))
                        additional_stops.append((pos - 1, charger, charge_amount))
                        battery_after_customer = temp_battery_at_pos - dist_to_charger * inputs.discharge_rate + charge_amount - dist_to_customer * inputs.discharge_rate
                        temp_battery_at_pos = temp_battery_at_pos - dist_to_charger * inputs.discharge_rate + charge_amount
                        visited_charging_since_last_customer.append(charger)
                    
                    # Battery check to next location or charger
                    if next_loc and not new_trip:
                        dist_to_next = inputs.distance_matrix[customer_to_insert][next_loc]
                        battery_after_next = battery_after_customer - dist_to_next * inputs.discharge_rate
                        if battery_after_next < 0:
                            charger = find_nearest_charger(customer_to_insert, inputs, visited_charging_since_last_customer)
                            dist_to_charger = inputs.distance_matrix[customer_to_insert][charger]
                            if battery_after_customer < dist_to_charger * inputs.discharge_rate:
                                continue
                            charge_amount = min(dist_to_next * inputs.discharge_rate - battery_after_customer + 1,
                                              inputs.max_battery_capacity - (battery_after_customer - dist_to_charger * inputs.discharge_rate))
                            additional_stops.append((pos, charger, charge_amount))
                            visited_charging_since_last_customer.append(charger)
                    elif new_trip:
                        total_dist_new_trip = inputs.distance_matrix[0][customer_to_insert] + inputs.distance_matrix[customer_to_insert][0]
                        if vehicle.initial_battery - total_dist_new_trip * inputs.discharge_rate < 0:
                            continue
                    
                    # Apply insertion to temporary vehicle
                    temp_vehicle = copy.deepcopy(vehicle)
                    for stop_pos, stop_loc, charge_amount in sorted(additional_stops, key=lambda x: x[0], reverse=True):
                        route_copy.insert(stop_pos, stop_loc)
                        charging_copy.insert(stop_pos, charge_amount)
                    insert_pos = pos + len([s for s in additional_stops if s[0] < pos])
                    route_copy.insert(insert_pos, customer_to_insert)
                    charging_copy.insert(insert_pos, 0)
                    
                    if new_trip:
                        temp_vehicle.routes[trip_idx] = route_copy
                        temp_vehicle.charging_quantity[trip_idx] = charging_copy
                        temp_vehicle.routes.append(new_trip)
                        temp_vehicle.charging_quantity.append(new_charging)
                        temp_vehicle.capacities.append(customer_demand)
                        temp_vehicle.lengths.append(inputs.distance_matrix[0][customer_to_insert] + inputs.distance_matrix[customer_to_insert][0])
                    else:
                        temp_vehicle.routes[trip_idx] = route_copy
                        temp_vehicle.charging_quantity[trip_idx] = charging_copy
                        temp_vehicle.customers[trip_idx] = [loc if loc in inputs.customers else loc for loc in route_copy]
                        temp_vehicle.capacities[trip_idx] = sum(inputs.customers[loc][5] for loc in temp_vehicle.customers[trip_idx] if loc in inputs.customers)
                        temp_vehicle.lengths[trip_idx] = sum(inputs.distance_matrix[route_copy[i]][route_copy[i+1]] for i in range(len(route_copy)-1))
                    
                    # Calculate incremental cost
                    temp_vehicle.unloading_completion_time = determine_unloading_completion_time(temp_vehicle, inputs)
                    penalty_cust, penalty_depot = evaluate_penalty_costs(temp_vehicle, inputs)
                    locker_cost = evaluate_locker_costs(temp_vehicle, inputs)
                    deployment_cost = evaluate_vehicle_deployment_costs(temp_vehicle, inputs)
                    travel_cost = evaluate_travel_costs(temp_vehicle, inputs)
                    total_cost = penalty_cust + penalty_depot + locker_cost + deployment_cost + travel_cost
                    incr_cost = total_cost - base_total_cost
                    
                    feasible_insertions.append((vid, trip_idx, pos, additional_stops, new_trip, new_charging, incr_cost))
        
        # Only consider new trip if no feasible insertion into existing trips
        if not feasible_insertions:
            for vid, vehicle in new_vehicles.items():
                base_vehicle = copy.deepcopy(vehicle)
                base_total_cost = 0
                if base_vehicle.routes and base_vehicle.routes[0] != [0, 0]:
                    base_vehicle.unloading_completion_time = determine_unloading_completion_time(base_vehicle, inputs)
                    base_penalty_cust, base_penalty_depot = evaluate_penalty_costs(base_vehicle, inputs)
                    base_locker_cost = evaluate_locker_costs(base_vehicle, inputs)
                    base_deployment_cost = evaluate_vehicle_deployment_costs(base_vehicle, inputs)
                    base_travel_cost = evaluate_travel_costs(base_vehicle, inputs)
                    base_total_cost = base_penalty_cust + base_penalty_depot + base_locker_cost + base_deployment_cost + base_travel_cost
                
                new_route = [0, customer_to_insert, 0]
                total_dist = inputs.distance_matrix[0][customer_to_insert] + inputs.distance_matrix[customer_to_insert][0]
                customer_demand = inputs.customers[customer_to_insert][5]
                if (vehicle.initial_battery - total_dist * inputs.discharge_rate >= 0 and 
                    customer_demand <= inputs.max_vehicle_volume):
                    temp_vehicle = copy.deepcopy(vehicle)
                    if temp_vehicle.routes[0] == [0, 0]:
                        temp_vehicle.routes[0] = new_route
                        temp_vehicle.charging_quantity[0] = [0, 0, 0]
                        temp_vehicle.capacities[0] = customer_demand
                        temp_vehicle.lengths[0] = total_dist
                    else:
                        temp_vehicle.routes.append(new_route)
                        temp_vehicle.charging_quantity.append([0, 0, 0])
                        temp_vehicle.capacities.append(customer_demand)
                        temp_vehicle.lengths.append(total_dist)
                    temp_vehicle.unloading_completion_time = determine_unloading_completion_time(temp_vehicle, inputs)
                    penalty_cust, penalty_depot = evaluate_penalty_costs(temp_vehicle, inputs)
                    locker_cost = evaluate_locker_costs(temp_vehicle, inputs)
                    deployment_cost = evaluate_vehicle_deployment_costs(temp_vehicle, inputs)
                    travel_cost = evaluate_travel_costs(temp_vehicle, inputs)
                    total_cost = penalty_cust + penalty_depot + locker_cost + deployment_cost + travel_cost
                    incr_cost = total_cost - base_total_cost
                    feasible_insertions.append((vid, trip_idx if 'trip_idx' in locals() else 0, 1, [], new_route, [0, 0, 0], incr_cost))
        
        # Select best insertion and apply
        inserted = False
        if feasible_insertions:
            best_insertion = min(feasible_insertions, key=lambda x: x[6])  # Minimize incremental cost
            vid, trip_idx, pos, additional_stops, new_trip, new_charging, _ = best_insertion
            if trip_idx != -1:  # Existing trip modification
                route_copy = new_vehicles[vid].routes[trip_idx].copy()
                charging_copy = new_vehicles[vid].charging_quantity[trip_idx].copy()
                for stop_pos, stop_loc, charge_amount in sorted(additional_stops, key=lambda x: x[0], reverse=True):
                    route_copy.insert(stop_pos, stop_loc)
                    charging_copy.insert(stop_pos, charge_amount)
                insert_pos = pos + len([s for s in additional_stops if s[0] < pos])
                route_copy.insert(insert_pos, customer_to_insert)
                charging_copy.insert(insert_pos, 0)
                new_vehicles[vid].routes[trip_idx] = route_copy
                new_vehicles[vid].customers[trip_idx] = [loc if loc in inputs.customers else loc for loc in route_copy]
                new_vehicles[vid].charging_quantity[trip_idx] = charging_copy
                new_vehicles[vid].capacities[trip_idx] = sum(inputs.customers[loc][5] for loc in new_vehicles[vid].customers[trip_idx] if loc in inputs.customers)
                new_vehicles[vid].lengths[trip_idx] = sum(inputs.distance_matrix[route_copy[i]][route_copy[i+1]] for i in range(len(route_copy)-1))
            else:  # New trip
                if new_vehicles[vid].routes[0] == [0, 0]:
                    new_vehicles[vid].routes[0] = new_trip
                    new_vehicles[vid].charging_quantity[0] = new_charging
                    new_vehicles[vid].capacities[0] = inputs.customers[customer_to_insert][5]
                    new_vehicles[vid].lengths[0] = inputs.distance_matrix[0][customer_to_insert] + inputs.distance_matrix[customer_to_insert][0]
                else:
                    new_vehicles[vid].routes.append(new_trip)
                    new_vehicles[vid].charging_quantity.append(new_charging)
                    new_vehicles[vid].capacities.append(inputs.customers[customer_to_insert][5])
                    new_vehicles[vid].lengths.append(inputs.distance_matrix[0][customer_to_insert] + inputs.distance_matrix[customer_to_insert][0])
            print(f"Inserted {customer_to_insert} into Vehicle {vid}, Trip {trip_idx if trip_idx != -1 else len(new_vehicles[vid].routes)-1}: {new_vehicles[vid].routes[trip_idx if trip_idx != -1 else len(new_vehicles[vid].routes)-1]}")
            inserted = True
        else:
            # Fallback to original position
            for orig_vid, orig_vehicle in original_vehicles.items():
                for orig_trip_idx, orig_route in enumerate(orig_vehicle.routes):
                    if customer_to_insert in orig_route:
                        pos = orig_route.index(customer_to_insert)
                        route_copy = orig_vehicle.routes[orig_trip_idx].copy()
                        charging_copy = orig_vehicle.charging_quantity[orig_trip_idx].copy()
                        new_vehicles[orig_vid].routes[orig_trip_idx] = route_copy
                        new_vehicles[orig_vid].customers[orig_trip_idx] = [loc if loc in inputs.customers else loc for loc in route_copy]
                        new_vehicles[orig_vid].charging_quantity[orig_trip_idx] = charging_copy
                        new_vehicles[orig_vid].capacities[orig_trip_idx] = sum(inputs.customers[loc][5] for loc in new_vehicles[orig_vid].customers[orig_trip_idx] if loc in inputs.customers)
                        new_vehicles[orig_vid].lengths[orig_trip_idx] = sum(inputs.distance_matrix[route_copy[i]][route_copy[i+1]] for i in range(len(route_copy)-1))
                        print(f"Fallback: Inserted {customer_to_insert} into original position in Vehicle {orig_vid}, Trip {orig_trip_idx}: {route_copy}")
                        inserted = True
                        break
                if inserted:
                    break
        
        if inserted and customer_to_insert in not_inserted:
            not_inserted.remove(customer_to_insert)
            assigned_customers.add(customer_to_insert)
    
    # Final updates and reporting for all vehicles
    print("\nFinal Solution After Repair:")
    total_costs = 0
    locker_costs = 0
    vehicle_deployment_costs = 0
    travel_costs = 0
    penalty_costs_customer = 0
    penalty_costs_depot = 0
    
    for vid in new_vehicles:
        vehicle = new_vehicles[vid]
        if vehicle.routes:
            # Recalculate charging quantities with minimal charging
            for trip_idx, route in enumerate(vehicle.routes):
                temp_battery = vehicle.initial_battery  # Start with initial battery
                new_charging = [0] * len(route)  # Initialize charging quantities
                
                # Simulate battery level step by step
                for i in range(1, len(route)):
                    # Calculate distance to next location and battery consumption
                    dist = inputs.distance_matrix[route[i-1]][route[i]]
                    temp_battery -= dist * inputs.discharge_rate
                    
                    # Check if current location is a charger or depot (excluding start/end unless charging needed)
                    if (route[i] in inputs.chargers or (route[i] == 0 and i != 0 and i != len(route) - 1)):
                        # Calculate minimal charge needed to reach next location or depot
                        next_dist = inputs.distance_matrix[route[i]][route[i+1]] if i + 1 < len(route) else 0
                        battery_needed = next_dist * inputs.discharge_rate
                        
                        # Charge if current battery is insufficient for next segment
                        if temp_battery < battery_needed:
                            charge_amount = min(battery_needed - temp_battery + 1, 
                                              inputs.max_battery_capacity - temp_battery)
                            new_charging[i] = charge_amount
                            temp_battery += charge_amount
                        # Charge if battery is negative (safety check)
                        elif temp_battery < 0:
                            charge_amount = min(-temp_battery + 1, 
                                              inputs.max_battery_capacity - temp_battery)
                            new_charging[i] = charge_amount
                            temp_battery += charge_amount
                    
                    # Warn if battery becomes infeasible
                    if temp_battery < 0:
                        print(f"Warning: Battery infeasible for Vehicle {vid}, Trip {trip_idx} at {route[i]}")
                
                # Update vehicle's charging quantities and route length
                vehicle.charging_quantity[trip_idx] = new_charging
                vehicle.lengths[trip_idx] = sum(inputs.distance_matrix[route[i]][route[i+1]] 
                                              for i in range(len(route)-1))
            
            # Update unloading completion time and costs
            vehicle.unloading_completion_time = determine_unloading_completion_time(vehicle, inputs)
            for trip_idx, route in enumerate(vehicle.routes):
                print(f"Vehicle {vid} Route {trip_idx}: {' '.join(map(str, route))}")
                print(f"Vehicle {vid} Charging Quantity {trip_idx}: {' '.join(map(str, 
                      [round(q, 6) for q in vehicle.charging_quantity[trip_idx]]))}")
                print(f"Vehicle {vid} Unloading Completion Time {trip_idx}: {' '.join(map(str, 
                      [round(t, 6) for t in vehicle.unloading_completion_time[trip_idx]]))}")
            
            penalty_cust, penalty_depot = evaluate_penalty_costs(vehicle, inputs)
            locker_cost = evaluate_locker_costs(vehicle, inputs)
            deployment_cost = evaluate_vehicle_deployment_costs(vehicle, inputs)
            travel_cost = evaluate_travel_costs(vehicle, inputs)
            
            penalty_costs_customer += penalty_cust
            penalty_costs_depot += penalty_depot
            locker_costs += locker_cost
            vehicle_deployment_costs += deployment_cost
            travel_costs += travel_cost
        else:
            print(f"Vehicle {vid} Route: (No routes assigned)")
    
    total_costs = penalty_costs_customer + penalty_costs_depot + locker_costs + vehicle_deployment_costs + travel_costs
    print(f"\nTotal Costs: {total_costs}")
    print(f"Locker Costs: {locker_costs}")
    print(f"Vehicle Deployment Costs: {vehicle_deployment_costs}")
    print(f"Travel Costs: {travel_costs}")
    print(f"Penalty Costs Customer: {penalty_costs_customer}")
    print(f"Penalty Costs Depot: {penalty_costs_depot}")
    
    if not_inserted:
        print(f"Error: Failed to insert customers {not_inserted}")
    else:
        print("All customers successfully inserted")
    
    return new_vehicles, not_inserted