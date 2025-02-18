def determine_unloading_completion_time(vehicle,inputs):
    unloading_completion_times = []
    for route in range(len(vehicle.routes)):
        unloading_completion_times.append([])
        time = vehicle.charging_quantity[route][0]
        for loc in range(len(vehicle.routes[route])):
            if vehicle.routes[route][loc] == 0:
                time += inputs.distance_matrix[vehicle.routes[route][loc - 1]][vehicle.routes[route][loc]] / inputs.speed 
                time += vehicle.charging_quantity[route][loc]
            if vehicle.routes[route][loc] in list(inputs.customers.keys()):
                time += inputs.distance_matrix[vehicle.routes[route][loc - 1]][vehicle.routes[route][loc]] / inputs.speed 
                time += inputs.customers[vehicle.routes[route][loc]][3]                
            if vehicle.routes[route][loc] in list(inputs.chargers.keys()):
                time += inputs.distance_matrix[vehicle.routes[route][loc - 1]][vehicle.routes[route][loc]] / inputs.speed 
                time += vehicle.charging_quantity[route][loc]
            if vehicle.routes[route][loc] in list(inputs.lockers.keys()):
                time += inputs.distance_matrix[vehicle.routes[route][loc - 1]][vehicle.routes[route][loc]] / inputs.speed 
                if [vehicle.routes[route][loc]] != [vehicle.routes[route][loc - 1]]:
                    time += inputs.lockers[vehicle.routes[route][loc]][3]     
            unloading_completion_times[route].append(time)
    return unloading_completion_times

