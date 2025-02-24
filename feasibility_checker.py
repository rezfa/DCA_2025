def check_solution_feasibility(solution_file, inputs, vehicles):
    """
    Checks the feasibility of a solution based on the solution file.
    
    Feasibility checks include:
      1. Each route must start and end at the depot (node 0).
      2. Every node in a route is valid (i.e., depot, or a key in inputs.customers, inputs.chargers, or inputs.lockers).
      3. The number of charging entries equals the number of route nodes.
      4. Battery simulation: For each leg, the battery is reduced by (distance * inputs.discharge_rate) and increased by the charging amount.
         The battery must never drop below zero nor exceed inputs.max_battery_capacity.
      5. For each segment (between depot visits), the cumulative visited customer demand (from inputs.customers[node][5]) does not exceed inputs.max_vehicle_volume.
      6. Each customer is visited exactly once for home delivery (locker indicator = 0), and not visited if designated for locker delivery.
      7. For any customer with a nonzero locker indicator, the indicated locker must exist and appear in at least one route.
      8. Each customer assigned to locker must be within the radius of that locker
    
    Returns:
      A tuple (is_feasible, messages), where is_feasible is True if the solution passes all checks,
      and messages is either "Solution is feasible." or a list of error messages.
    """
    
    errors = []
    

    # Read the solution file and generate solution_lines
    try:
        with open(solution_file, "r") as f:
            solution_lines = f.read().splitlines()
    except Exception as e:
        return False, [f"Error reading solution file: {e}"]
    
    # Header Parsing (first 10 lines expected)
    if len(solution_lines) < 10:
        errors.append("Header incomplete: less than 10 lines in the solution file.")
        return False, errors
    
    instance_id = solution_lines[0].strip()
    # Line 1 is empty, line 2 is the feasibility flag (ignored)
    # Lines 3-8 contain cost information (ignored for feasibility)
    locker_delivery_line = solution_lines[9].strip()
    try:
        locker_delivery = list(map(int, locker_delivery_line.split()))
    except Exception as e:
        errors.append("Error parsing locker delivery line: " + str(e))
        locker_delivery = []
    

    # Parse vehicle solution blocks (each vehicle has 3 lines starting at line 10)
    vehicle_solutions = {}  # key: vehicle id, value: dict with 'route', 'charging', 'unloading'
    line_index = 10
    while line_index + 2 < len(solution_lines):
        # Parse route line
        route_line = solution_lines[line_index].strip().split()
        try:
            veh_id = int(route_line[0])
            # To allow values like "0.0" to be interpreted as integer 0
            route = [int(float(x)) for x in route_line[1:]]
        except Exception as e:
            errors.append(f"Error parsing route line at line {line_index+1}: {e}")
            route = []
            veh_id = None
        
        # Parse charging line
        charging_line = solution_lines[line_index+1].strip().split()
        try:
            charging_id = int(charging_line[0])
            charging = list(map(float, charging_line[1:]))
        except Exception as e:
            errors.append(f"Error parsing charging line at line {line_index+2}: {e}")
            charging = []
        
        # Parse unloading times line (informational)
        unloading_line = solution_lines[line_index+2].strip().split()
        try:
            unloading_id = int(unloading_line[0])
            unloading = list(map(float, unloading_line[1:]))
        except Exception as e:
            errors.append(f"Error parsing unloading line at line {line_index+3}: {e}")
            unloading = []
        
        if veh_id is not None:
            vehicle_solutions[veh_id] = {
                'route': route,
                'charging': charging,
                'unloading': unloading
            }
        
        line_index += 3  # Move to the next vehicle block
    

    # Global customer visit count (for home deliveries)
    customer_visit_count = {}  # key: customer id, value: count of visits

    # Per-vehicle checks
    for vid, sol in vehicle_solutions.items():
        route = sol['route']
        charging = sol['charging']
        
        # (1) Check that the route is nonempty and starts/ends at depot (node 0)
        if not route:
            errors.append(f"Vehicle {vid}: Route is empty.")
            continue
        if route[0] != 0:
            errors.append(f"Vehicle {vid} (Route step 1): Route does not start at depot (found {route[0]}).")
        if route[-1] != 0:
            errors.append(f"Vehicle {vid} (Route final step): Route does not end at depot (found {route[-1]}).")
        
        # (2) Validate each node in the route
        for pos, node in enumerate(route):
            if node != 0 and (node not in inputs.customers and node not in inputs.chargers and node not in inputs.lockers):
                errors.append(f"Vehicle {vid} (Route node {pos+1}): Node {node} is invalid.")
        
        # (3) Check that the number of charging entries equals the number of route nodes.
        if len(route) != len(charging):
            errors.append(f"Vehicle {vid}: Mismatch between route nodes ({len(route)}) and charging entries ({len(charging)}).")
        
        # (4) Simulate battery consumption along the route.
        initial_battery = vehicles[vid].initial_battery if vid in vehicles else inputs.max_battery_capacity
        battery = initial_battery
        for i in range(1, len(route)):
            prev_node = route[i-1]
            curr_node = route[i]
            try:
                distance = inputs.distance_matrix[prev_node][curr_node]
            except Exception as e:
                errors.append(f"Vehicle {vid} (Battery simulation {prev_node}->{curr_node}): Error retrieving distance: {e}.")
                distance = 0
            consumption = distance * inputs.discharge_rate
            if battery < consumption:
                errors.append(
                    f"Vehicle {vid} (Battery check {prev_node}->{curr_node}): Battery ({battery:.2f}) insufficient for consumption ({consumption:.2f})."
                )
                break
            battery -= consumption
            charge = charging[i]
            if charge < 0:
                errors.append(f"Vehicle {vid} (Charging at {curr_node}): Negative charging amount ({charge}).")
            battery += charge
            if battery > inputs.max_battery_capacity:
                errors.append(
                    f"Vehicle {vid} (Charging at {curr_node}): Battery ({battery:.2f}) exceeds max capacity ({inputs.max_battery_capacity})."
                )
                battery = inputs.max_battery_capacity
        
        # (5) Check capacity per segment (between depot visits)
        segment_demand = 0
        for pos, node in enumerate(route):
            if node == 0:
                if segment_demand > inputs.max_vehicle_volume:
                    errors.append(
                        f"Vehicle {vid} (Capacity at depot at position {pos+1}): Segment demand {segment_demand} exceeds max volume ({inputs.max_vehicle_volume})."
                    )
                segment_demand = 0
            elif node in inputs.customers:
                demand = inputs.customers[node][5]  # customer demand assumed at index 5
                segment_demand += demand
        if segment_demand > inputs.max_vehicle_volume:
            errors.append(
                f"Vehicle {vid}: Final segment demand {segment_demand} exceeds max volume ({inputs.max_vehicle_volume})."
            )
        
        # (6) Record customer visits for global check
        for node in route:
            if node in inputs.customers:
                customer_visit_count[node] = customer_visit_count.get(node, 0) + 1
    
    # Global customer visit and locker delivery checks
    for cust in inputs.customers.keys():
        try:
            # Assumes the locker_delivery list is ordered by customer id (1-indexed)
            indicator = locker_delivery[cust - 1]
        except Exception as e:
            errors.append(f"Global check: Could not retrieve locker indicator for customer {cust}: {e}.")
            indicator = 0
        
        count = customer_visit_count.get(cust, 0)
        if indicator == 0:
            if count != 1:
                errors.append(f"Global check: Customer {cust} (home delivery) is visited {count} times (expected 1).")
        else:
            if count != 0:
                errors.append(f"Global check: Customer {cust} is marked for locker delivery (indicator {indicator}) but appears {count} times in routes.")
            if indicator not in inputs.lockers:
                errors.append(f"Locker consistency: For customer {cust}, indicated locker {indicator} is invalid.")
            else:
                locker_found = any(indicator in sol['route'] for sol in vehicle_solutions.values())
                if not locker_found:
                    errors.append(f"Locker consistency: For customer {cust}, indicated locker {indicator} is not visited in any route.")
                else:
                    # Additional check: verify customer is within locker radius.
                    cust_coords = inputs.customers[cust]
                    locker_coords = inputs.lockers[indicator]
                    dx = cust_coords[1] - locker_coords[1]
                    dy = cust_coords[2] - locker_coords[2]
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance > inputs.locker_radius:
                        errors.append(
                            f"Locker radius check: Customer {cust} (at ({cust_coords[1]:.2f}, {cust_coords[2]:.2f})) "
                            f"is not within radius of locker {indicator} (at ({locker_coords[1]:.2f}, {locker_coords[2]:.2f})); "
                            f"distance = {distance:.2f}, radius = {inputs.locker_radius}."
                        )
    
    # ---------------------------
    # Return the final results
    # ---------------------------
    if errors:
        return False, errors
    else:
        return True, "Solution is feasible."
