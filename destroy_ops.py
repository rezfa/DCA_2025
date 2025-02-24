import random
import copy

def random_removal_operator(vehicles, inputs, removal_rate=0.2, random_seed=None):
    """
    Random removal destroy operator.
    
    This operator randomly removes a percentage (removal_rate) of customer nodes 
    from each vehicle's routes. It only removes nodes that are customers (as defined in inputs.customers)
    and never removes depot nodes (0) or other nodes (e.g., chargers or lockers).
    
    Parameters:
      vehicles: A dictionary mapping vehicle IDs to Vehicles objects.
                Each Vehicles object contains attributes such as 'routes' (list of trips),
                'charging_quantity' (list of lists aligned with routes), 'capacities', etc.
      inputs: An instance of the Inputs class. This is used to determine which nodes are customers.
      removal_rate: Float in [0,1]. The percentage of customer nodes to remove from each route.
      random_seed: Optional integer seed for reproducibility.
      
    Returns:
      new_vehicles: A deep copy of the vehicles dictionary, with the selected customer nodes removed.
      removed_customers: A list of tuples (vehicle_id, route_index, customer_node) representing the removed nodes.
    """
    
    if random_seed is not None:
        random.seed(random_seed)
    
    new_vehicles = copy.deepcopy(vehicles)
    removed_customers = []
    
    # Iterate over each vehicle in the solution.
    for vid, vehicle in new_vehicles.items():
        # Iterate over each trip (route) in this vehicle.
        for route_index, route in enumerate(vehicle.routes):
            # Identify indices of nodes that are customers.
            customer_indices = [i for i, node in enumerate(route) if node in inputs.customers]
            # Calculate the number of customers to remove (round down).
            num_to_remove = int(len(customer_indices) * removal_rate)
            if num_to_remove < 1 and len(customer_indices) > 0:
                num_to_remove = 1

            if num_to_remove > 0:
                # Randomly choose indices (from the candidate customer indices) to remove.
                indices_to_remove = random.sample(customer_indices, num_to_remove)
                # Remove in descending order to preserve correct indices.
                for idx in sorted(indices_to_remove, reverse=True):
                    removed_node = route[idx]
                    removed_customers.append((vid, route_index, removed_node))
                    # Remove the customer node from the route.
                    del route[idx]
                    # Remove the corresponding charging entry.
                    del vehicle.charging_quantity[route_index][idx]
                    # Optionally update capacity for that route:
                    if vehicle.capacities and len(vehicle.capacities) > route_index:
                        demand = inputs.customers[removed_node][5]  # assuming demand is stored at index 5
                        vehicle.capacities[route_index] -= demand
                    # You could also update route lengths here if desired,
                    # or recompute them later in a separate evaluation function.
    
    return new_vehicles, removed_customers
