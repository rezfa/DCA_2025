
def initial_solution(Inputs):
    """Constructs an initial feasible solution for the problem, tracking time at each node and calculating objective function."""
    route = []
    trips = []
    total_distance = 0
    vehicle_count = 0
    
    for vehicle in Inputs.vehicles:
        vehicle_id = vehicle[0]
        soc = vehicle[1]
        load = Inputs.max_vehicle_volume
        depot = Inputs.depot
        unvisited_customers = {customer[0] for customer in Inputs.customers}
        locations = []  # Store locations separately
        times = []  # Store time at each node separately
        soc_levels = []  # Store SOC at each node separately
        current_location = depot
        time = 0  # Initialize time tracking
        
        while unvisited_customers:
            trip_locations = [current_location]
            trip_times = [time]
            trip_soc = [soc]
            vehicle_count += 1
            
            while unvisited_customers:
                target = find_nearest_customer(current_location, unvisited_customers, Inputs)
                travel_time = distance(current_location, target) / Inputs.vehicle_speed
                total_distance += distance(current_location, target)
                
                # Check if we can reach target
                if soc < distance(current_location, target) * Inputs.discharge_rate:
                    nearest_charger = find_nearest_charger(current_location, Inputs)
                    travel_time_to_charger = distance(current_location, nearest_charger) / Inputs.vehicle_speed
                    required_charge = max(0, min((distance(nearest_charger, depot) + distance(nearest_charger, target)) * Inputs.discharge_rate - soc, Inputs.max_battery_capacity - soc))
                    charge_time = required_charge / Inputs.recharge_rate
                    trip_locations.append(nearest_charger)
                    trip_times.append(time + travel_time_to_charger + charge_time)
                    trip_soc.append(min(soc + required_charge, Inputs.max_battery_capacity))
                    soc = min(soc + required_charge, Inputs.max_battery_capacity)
                    time += travel_time_to_charger + charge_time
                
                # Check if we can return after serving customer
                if soc < (distance(current_location, target) + distance(target, find_nearest_charger(target, Inputs))) * Inputs.discharge_rate:
                    nearest_charger = find_nearest_charger(current_location, Inputs)
                    travel_time_to_charger = distance(current_location, nearest_charger) / Inputs.vehicle_speed
                    required_charge = max(0, min((distance(nearest_charger, depot)) * Inputs.discharge_rate - soc, Inputs.max_battery_capacity - soc))
                    charge_time = required_charge / Inputs.recharge_rate
                    trip_locations.append(nearest_charger)
                    trip_times.append(time + travel_time_to_charger + charge_time)
                    trip_soc.append(min(soc + required_charge, Inputs.max_battery_capacity))
                    soc = min(soc + required_charge, Inputs.max_battery_capacity)
                    time += travel_time_to_charger + charge_time
                
                # Check load capacity
                if load < Inputs.customer_demands[target]:
                    trip_locations.append(depot)
                    trip_times.append(time)
                    trip_soc.append(soc)
                    load = Inputs.max_vehicle_volume
                    soc = vehicle[1]
                    time += Inputs.depot_service_time
                
                # Visit customer
                trip_locations.append(target)
                trip_times.append(time + travel_time)
                trip_soc.append(soc)
                unvisited_customers.remove(target)
                load = max(0, min(load - Inputs.customer_demands[target], Inputs.max_vehicle_volume))
                soc = max(0, soc - distance(current_location, target) * Inputs.discharge_rate)
                time += travel_time + Inputs.service_time[target]
                current_location = target
            
            # Return to depot
            travel_time_to_depot = distance(current_location, depot) / Inputs.vehicle_speed
            total_distance += distance(current_location, depot)
            trip_locations.append(depot)
            trip_times.append(time + travel_time_to_depot)
            trip_soc.append(soc)
            trips.append((vehicle_id, trip_locations, trip_times, trip_soc))
            soc = vehicle[1]
            load = Inputs.max_vehicle_volume
            current_location = depot
            time += travel_time_to_depot
        
        route.append(trips)
    
    # Calculate objective function
    penalty_customer_late = sum(max(0, arrival_time - Inputs.customer_deadlines[node]) * Inputs.penalty_per_time_unit for trip in trips for node, arrival_time in zip(trip[1], trip[2]) if node in Inputs.customer_deadlines)
    penalty_depot_late = max(0, trips[-1][2][-1] - Inputs.depot_deadline) * Inputs.penalty_per_time_unit if trips else 0
    total_cost = (vehicle_count * Inputs.vehicle_deployment_cost) + (penalty_customer_late + penalty_depot_late) + (total_distance * Inputs.cost_per_distance)
    
    return route, trips, total_cost