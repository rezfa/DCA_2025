from load_data import load_instance, Vehicles
from initial_solution import initial_solution
from evaluate_solution import determine_unloading_completion_time, evaluate_penalty_costs, evaluate_locker_costs, evaluate_vehicle_deployment_costs, evaluate_travel_costs, locker_delivery
from write_solution_file import write_solution_file
from ALNS import ALNS
from feasibility_checker import check_solution_feasibility_from_dict


#TO DO:
    # Feasibility check returns 1 if a customers is missing
    # Create repair operator

instance_id = 996
inputs_data = f"Toys/Not Annotated/{instance_id}.inst"

inputs = load_instance(inputs_data)

vehicles = {i+1: Vehicles(vehicle_id=veh[0], initial_battery=veh[1]) for i, veh in enumerate(inputs.vehicles)}

initial_vehicles = initial_solution(inputs, vehicles)

max_iterations = 1000
initial_temperature = 1000
learning_rate = 0.15
cooling_rate = 0.95
segment_length = 100
sigma1 = 5
sigma2 = 2
sigma3 = 1

vehicles = ALNS(inputs, initial_vehicles, max_iterations, initial_temperature, learning_rate, cooling_rate, segment_length, sigma1, sigma2, sigma3)

# Write the solution file
instance_description = ""
feasible = check_solution_feasibility_from_dict(vehicles, inputs)[0]  
locker_delivery = locker_delivery(vehicles,inputs)

penalty_costs_customer = sum(vehicles[vehicle].penalty_costs_customer for vehicle in vehicles.keys())
penalty_costs_depot = sum(vehicles[vehicle].penalty_costs_depot for vehicle in vehicles.keys())
locker_costs = sum(vehicles[vehicle].locker_costs for vehicle in vehicles.keys()) 
vehicle_deployment_costs = sum(vehicles[vehicle].vehicle_deployment_costs for vehicle in vehicles.keys())
travel_costs = sum(vehicles[vehicle].travel_costs for vehicle in vehicles.keys())
total_costs = penalty_costs_customer + penalty_costs_depot + locker_costs + vehicle_deployment_costs + travel_costs
 
write_solution_file(instance_id, instance_description, feasible, total_costs, locker_costs, 
                        vehicle_deployment_costs, travel_costs, penalty_costs_customer, penalty_costs_depot, 
                        locker_delivery, vehicles)


