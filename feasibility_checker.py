def check_solution_feasibility_from_dict(vehicles, inputs):
    """
    Checks the feasibility of a given solution represented as a dictionary of vehicle routes.
    This function is adapted to work with intermediate solutions (e.g., outputs of repair operators).
    """
    errors = []
    
    # Global customer visit count
    customer_visit_count = {}
    
    for vid, vehicle in vehicles.items():
        for trip_idx, route in enumerate(vehicle.routes):
            charging = vehicle.charging_quantity[trip_idx]
            
            # (1) Check start and end at depot
            if route[0] != 0:
                errors.append(f"Vehicle {vid} Trip {trip_idx}: Does not start at depot (found {route[0]}).")
            if route[-1] != 0:
                errors.append(f"Vehicle {vid} Trip {trip_idx}: Does not end at depot (found {route[-1]}).")
            
            # (2) Validate nodes in route
            for pos, node in enumerate(route):
                if node != 0 and node not in inputs.customers and node not in inputs.chargers and node not in inputs.lockers:
                    errors.append(f"Vehicle {vid} Trip {trip_idx}: Invalid node {node} at position {pos}.")
            
            # (3) Check charging consistency
            if len(route) != len(charging):
                errors.append(f"Vehicle {vid} Trip {trip_idx}: Mismatch between route nodes ({len(route)}) and charging entries ({len(charging)}).")
            
            # (4) Battery simulation
            battery = vehicle.initial_battery
            for i in range(1, len(route)):
                prev_node, curr_node = route[i-1], route[i]
                distance = inputs.distance_matrix[prev_node][curr_node]
                consumption = distance * inputs.discharge_rate
                battery -= consumption
                battery += charging[i]
                if battery < 0:
                    errors.append(f"Vehicle {vid} Trip {trip_idx}: Battery depleted at node {curr_node}.")
                if battery > inputs.max_battery_capacity:
                    errors.append(f"Vehicle {vid} Trip {trip_idx}: Battery exceeds max capacity at node {curr_node}.")
            
            # (5) Check vehicle capacity per trip
            total_demand = sum(inputs.customers[n][5] for n in route if n in inputs.customers)
            if total_demand > inputs.max_vehicle_volume:
                errors.append(f"Vehicle {vid} Trip {trip_idx}: Exceeds max vehicle capacity ({inputs.max_vehicle_volume}).")
            
            # (6) Record customer visits
            for node in route:
                if node in inputs.customers:
                    customer_visit_count[node] = customer_visit_count.get(node, 0) + 1
    
    # Global check for customer deliveries
    for cust, count in customer_visit_count.items():
        if count != 1:
            errors.append(f"Customer {cust}: Visited {count} times (expected exactly once).")
    
    if errors:
        return 0, errors
    return 1, "Solution is feasible."

# Example usage:
# feasible, messages = check_solution_feasibility_from_dict(vehicles, inputs)
