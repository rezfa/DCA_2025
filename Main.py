from load_data import load_instance, Vehicles
from initial_solution import initial_solution
from evaluate_solution import determine_unloading_completion_time, evaluate_penalty_costs, evaluate_locker_costs, evaluate_vehicle_deployment_costs, evaluate_travel_costs, locker_delivery


instance_id = 929
inputs_data = f"Toys/Not Annotated/{instance_id}.inst"

inputs = load_instance(inputs_data)

vehicles = {i+1: Vehicles(vehicle_id=veh[0], initial_battery=veh[1]) for i, veh in enumerate(inputs.vehicles)}

vehicles = initial_solution(inputs, vehicles)

for vehicle in list(vehicles.keys()):
    vehicles[vehicle].unloading_completion_time = determine_unloading_completion_time(vehicles[vehicle],inputs)
    vehicles[vehicle].penalty_costs = evaluate_penalty_costs(vehicles[vehicle],inputs)
    vehicles[vehicle].locker_costs = evaluate_locker_costs(vehicles[vehicle],inputs)
    vehicles[vehicle].vehicle_deployment_costs = evaluate_vehicle_deployment_costs(vehicles[vehicle],inputs)
    vehicles[vehicle].travel_costs = evaluate_travel_costs(vehicles[vehicle],inputs)
    
  
total_penalty_costs = sum(vehicles[vehicle].penalty_costs for vehicle in vehicles.keys())
total_locker_costs = sum(vehicles[vehicle].locker_costs for vehicle in vehicles.keys()) 
total_vehicle_deployment_costs = sum(vehicles[vehicle].vehicle_deployment_costs for vehicle in vehicles.keys())
total_travel_costs = sum(vehicles[vehicle].travel_costs for vehicle in vehicles.keys())
total_costs = total_penalty_costs + total_locker_costs + total_vehicle_deployment_costs + total_travel_costs

