def write_solution_file(instance_id, instance_description, feasible, total_costs, locker_costs, 
                        vehicle_deployment_costs, travel_costs, penalty_costs_customer, penalty_costs_depot, 
                        locker_delivery, vehicles):
    filename = f"{instance_id}.sol"
    with open(filename, "w") as f:
        f.write(f"{instance_id}\n")
        f.write(f"{instance_description}\n")
        f.write(f"{feasible}\n")
        f.write(f"{total_costs}\n")
        f.write(f"{locker_costs}\n")
        f.write(f"{vehicle_deployment_costs}\n")
        f.write(f"{travel_costs}\n")
        f.write(f"{penalty_costs_customer}\n")
        f.write(f"{penalty_costs_depot}\n")
        
        f.write(" ".join(map(str, locker_delivery)) + "\n")  # Locker delivery indicators
        
        for vehicle in list(vehicles.keys()):
            # Flatten lists of lists
            route_flat = [vehicle] + [item for sublist in vehicles[vehicle].routes for item in sublist]
            charging_flat = [vehicle] + [item for sublist in vehicles[vehicle].charging_quantity for item in sublist]
            unloading_flat = [vehicle] + [item for sublist in vehicles[vehicle].unloading_completion_time for item in sublist]
        
            # Write to file
            f.write(" ".join(map(str, route_flat)) + "\n")
            f.write(" ".join(map(str, charging_flat)) + "\n")
            f.write(" ".join(map(str, unloading_flat)) + "\n")
        


