from load_data import load_instance, Vehicles
from initial_solution import initial_solution
from evaluate_solution import determine_unloading_completion_time, evaluate_penalty_costs, evaluate_locker_costs, evaluate_vehicle_deployment_costs, evaluate_travel_costs, locker_delivery
from write_solution_file import write_solution_file
from feasibility_checker import check_solution_feasibility
from destroy_ops import random_removal_operator
from repair_ops import greedy_insertion_operator


instance_id = 929
inputs_data = f"Toys/Not Annotated/{instance_id}.inst"

inputs = load_instance(inputs_data)

vehicles = {i+1: Vehicles(vehicle_id=veh[0], initial_battery=veh[1]) for i, veh in enumerate(inputs.vehicles)}

vehicles = initial_solution(inputs, vehicles)

for vehicle in list(vehicles.keys()):
    vehicles[vehicle].unloading_completion_time = determine_unloading_completion_time(vehicles[vehicle],inputs)
    vehicles[vehicle].penalty_costs_customer = evaluate_penalty_costs(vehicles[vehicle],inputs)[0]
    vehicles[vehicle].penalty_costs_depot = evaluate_penalty_costs(vehicles[vehicle],inputs)[1]
    vehicles[vehicle].locker_costs = evaluate_locker_costs(vehicles[vehicle],inputs)
    vehicles[vehicle].vehicle_deployment_costs = evaluate_vehicle_deployment_costs(vehicles[vehicle],inputs)
    vehicles[vehicle].travel_costs = evaluate_travel_costs(vehicles[vehicle],inputs)
 
    
instance_description = ""
feasible = 1  #add feasibility check later
  
penalty_costs_customer = sum(vehicles[vehicle].penalty_costs_customer for vehicle in vehicles.keys())
penalty_costs_depot = sum(vehicles[vehicle].penalty_costs_depot for vehicle in vehicles.keys())
locker_costs = sum(vehicles[vehicle].locker_costs for vehicle in vehicles.keys()) 
vehicle_deployment_costs = sum(vehicles[vehicle].vehicle_deployment_costs for vehicle in vehicles.keys())
travel_costs = sum(vehicles[vehicle].travel_costs for vehicle in vehicles.keys())
total_costs = penalty_costs_customer + penalty_costs_depot + locker_costs + vehicle_deployment_costs + travel_costs

locker_delivery = locker_delivery(vehicles,inputs)

write_solution_file(instance_id, instance_description, feasible, total_costs, locker_costs, 
                        vehicle_deployment_costs, travel_costs, penalty_costs_customer, penalty_costs_depot, 
                        locker_delivery, vehicles)

#############
# New addition
#############

new_vehicles1, removed_customers = random_removal_operator(vehicles, inputs, removal_rate=0.2, random_seed=None)
new_vehicles2, not_inserted = greedy_insertion_operator(vehicles, removed_customers, inputs)

print(removed_customers)
for vid, vehicle in new_vehicles2.items():
    print(f"Vehicle {vid} Routes:")
    for trip_index, route in enumerate(vehicle.routes):
        print(f"  Trip {trip_index}: {route}")


solution_file = "929.sol"
is_feasible, message = check_solution_feasibility(solution_file, inputs, vehicles)
if is_feasible:
    print("The solution is feasible.")
else:
    print("The solution is infeasible. Errors:")
    for error in message:
        print(error)