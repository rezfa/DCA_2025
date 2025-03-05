import random

def random_remove_customers(vehicles, inputs):
    removal_rate = 0.1
    
    # Calculate number of customers to remove
    num_to_remove = max(1, int(len(inputs.customers.keys()) * removal_rate))  # Ensure at least 1 is removed
    
    # Keep track of the removed customers
    removed_customers = []
    # Keep track of the vehicles that need recomputations of the costs
    affected_vehicles = []
    
    # Remove a random customer from a random route
    for _ in range(num_to_remove):
        while True: #select a vehicle that has at least one trip with customers in it
            vehicle = random.randint(1,len(vehicles.keys()))
            if any(len(trip) > 2 for trip in vehicles[vehicle].customers):
                break
        while True: #select a trip with customers in it
            trip = random.randrange(len(vehicles[vehicle].customers))
            if len(vehicles[vehicle].customers[trip]) > 2:
                break
        while True: #select a customer from the trip
            customer = random.randrange(1,len(vehicles[vehicle].customers[trip])-1)
            if customer in vehicles.keys():
                break
        affected_vehicles.append(vehicle)
        removed_customers.append(vehicles[vehicle].customers[trip][customer])
        vehicles[vehicle].customers[trip].pop(customer)
        vehicles[vehicle].routes[trip].pop(customer)
        vehicles[vehicle].charging_quantity[trip].pop(customer)
        vehicles[vehicle].capacities[trip] -= inputs.customers[customer][5]
    
    return vehicles, removed_customers, affected_vehicles