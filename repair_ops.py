import copy
import math

def greedy_insertion_operator(vehicles, removed_customers, inputs):
    """
    Greedy insertion repair operator.
    
    This operator attempts to reinsert each removed customer (from the destroy operator)
    into the current solution by evaluating all possible insertion positions across all vehicles'
    routes. It selects the position that minimizes the incremental route cost while ensuring that:
      - The vehicle capacity is not exceeded.
      - The battery consumption simulation remains feasible.
      
    Parameters:
      vehicles: A dictionary mapping vehicle IDs to Vehicles objects.
                Each Vehicles object includes attributes such as 'routes', 'charging_quantity',
                'capacities', and 'lengths'.
      removed_customers: A list of tuples (vehicle_id, route_index, customer_node) indicating the
                         removed customer nodes.
      inputs: An instance of the Inputs class (provides distance_matrix, customers, max_vehicle_volume,
              discharge_rate, etc.)
              
    Returns:
      new_vehicles: The updated vehicles dictionary with the removed customers reinserted where feasible.
      not_inserted: A list of customer nodes that could not be feasibly reinserted.
    """
    
    # Create a deep copy so we don't modify the original solution.
    new_vehicles = copy.deepcopy(vehicles)
    not_inserted = []
    
    # Helper function to check capacity feasibility for a candidate route.
    def is_capacity_feasible(route):
        # For a route (a trip, which starts and ends with depot), the total demand is the sum of demands for customer nodes.
        total_demand = sum(inputs.customers[node][5] for node in route if node in inputs.customers)
        return total_demand <= inputs.max_vehicle_volume

    # Helper function to check battery feasibility for a candidate route.
    # Here we simulate battery consumption along the route.
    def is_battery_feasible(route, initial_battery):
        battery = initial_battery
        for i in range(1, len(route)):
            prev_node = route[i-1]
            curr_node = route[i]
            try:
                distance = inputs.distance_matrix[prev_node][curr_node]
            except Exception:
                return False
            consumption = distance * inputs.discharge_rate
            if battery < consumption:
                return False
            battery -= consumption
            # Note: In our repair operator, inserted customer nodes get a charging placeholder of 0.
            # If your route contains charging stops, additional logic is needed.
        return True

    # For each removed customer, try to insert it in a greedy way.
    for (orig_vid, orig_route_index, customer) in removed_customers:
        best_insertion = None
        best_cost_increase = float('inf')
        best_vehicle_id = None
        best_route_index = None
        best_position = None
        
        # Try all vehicles and all trips.
        for vid, vehicle in new_vehicles.items():
            # Get the vehicle's initial battery (from original vehicles dictionary)
            init_battery = vehicles[vid].initial_battery if vid in vehicles else inputs.max_battery_capacity
            for r_index, route in enumerate(vehicle.routes):
                # Only consider routes with at least two nodes (should start and end with depot)
                if len(route) < 2:
                    continue
                # Try all insertion positions between 1 and len(route)-1.
                for pos in range(1, len(route)):
                    candidate_route = route[:pos] + [customer] + route[pos:]
                    
                    # Check capacity feasibility.
                    if not is_capacity_feasible(candidate_route):
                        continue
                    
                    # Check battery feasibility.
                    if not is_battery_feasible(candidate_route, init_battery):
                        continue
                    
                    # Calculate the cost increase (distance increase) due to insertion.
                    prev_node = route[pos - 1]
                    next_node = route[pos]
                    cost_increase = (inputs.distance_matrix[prev_node][customer] +
                                     inputs.distance_matrix[customer][next_node] -
                                     inputs.distance_matrix[prev_node][next_node])
                    
                    if cost_increase < best_cost_increase:
                        best_cost_increase = cost_increase
                        best_insertion = pos
                        best_vehicle_id = vid
                        best_route_index = r_index
                        
        # If a feasible insertion is found, perform the insertion.
        if best_insertion is not None:
            # Insert the customer in the chosen vehicle/route at the best insertion position.
            new_vehicles[best_vehicle_id].routes[best_route_index].insert(best_insertion, customer)
            # Insert a placeholder charging value of 0 at the same position.
            new_vehicles[best_vehicle_id].charging_quantity[best_route_index].insert(best_insertion, 0)
            # Update the capacity: increase the capacity usage by the customer's demand.
            if new_vehicles[best_vehicle_id].capacities and len(new_vehicles[best_vehicle_id].capacities) > best_route_index:
                new_vehicles[best_vehicle_id].capacities[best_route_index] += inputs.customers[customer][5]
            # Update the route length.
            new_length = 0
            route = new_vehicles[best_vehicle_id].routes[best_route_index]
            for i in range(1, len(route)):
                new_length += inputs.distance_matrix[route[i-1]][route[i]]
            new_vehicles[best_vehicle_id].lengths[best_route_index] = new_length
        else:
            # If no feasible insertion found, record the customer.
            not_inserted.append(customer)
    
    return new_vehicles, not_inserted