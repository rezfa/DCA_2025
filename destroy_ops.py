import random
import copy

def random_removal_operator(vehicles, inputs, removal_rate=0.5, random_seed=None):
    """
    Randomly removes a percentage of customers from vehicle routes.
    
    Parameters:
    - vehicles: Dict of Vehicles objects representing the current solution
    - inputs: Inputs object containing problem data (customers, distance matrix, etc.)
    - removal_rate: Fraction of customers to remove (default: 0.2)
    - random_seed: Seed for reproducibility (optional)
    
    Returns:
    - new_vehicles: Modified deep copy of vehicles with customers removed
    - removed_customers: List of customer IDs removed from the routes
    """
    if random_seed is not None:
        random.seed(random_seed)
    
    # Create a deep copy of vehicles to avoid modifying the original
    new_vehicles = {vid: copy.deepcopy(vehicle) for vid, vehicle in vehicles.items()}
    
    # Collect all customers currently in the solution
    all_customers = []
    for vehicle in new_vehicles.values():
        for route in vehicle.customers:
            for loc in route:
                if loc in inputs.customers.keys():
                    all_customers.append(loc)
    
    # Calculate number of customers to remove
    num_to_remove = max(1, int(len(all_customers) * removal_rate))  # Ensure at least 1 is removed
    removed_customers = random.sample(all_customers, num_to_remove)
    
    # Remove selected customers from routes and update related attributes
    for vehicle in new_vehicles.values():
        for route_idx in range(len(vehicle.routes)):
            # Filter out removed customers from the route
            new_route = [loc for loc in vehicle.routes[route_idx] if loc not in removed_customers]
            vehicle.routes[route_idx] = new_route
            # Update customers list accordingly
            vehicle.customers[route_idx] = [loc for loc in vehicle.customers[route_idx] if loc not in removed_customers]
            # Adjust capacities (subtract demand of removed customers)
            vehicle.capacities[route_idx] = sum(inputs.customers[loc][5] for loc in vehicle.customers[route_idx] if loc in inputs.customers.keys())
            # Reset lengths and charging quantities (to be recalculated later if needed)
            vehicle.lengths[route_idx] = 0  # Will need recalculation
            vehicle.charging_quantity[route_idx] = [0] * len(new_route)

    return new_vehicles, removed_customers