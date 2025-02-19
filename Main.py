from load_data import load_instance, Vehicles
from initial_solution import initial_solution
from evaluate_solution import determine_unloading_completion_time, evaluate_penalty_costs, evaluate_locker_costs, evaluate_vehicle_deployment_costs, evaluate_travel_costs, locker_delivery
from write_solution_file import write_solution_file

instance_id = 996
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

