import random
import math
import numpy as np
import copy
import matplotlib.pyplot as plt
from evaluate_solution import determine_unloading_completion_time, evaluate_penalty_costs, evaluate_locker_costs, evaluate_vehicle_deployment_costs, evaluate_travel_costs, compute_objective
from destroy_ops import random_remove_customers
from repair_ops import best_out_of_five_insertion
from feasibility_checker import check_solution_feasibility_from_dict


def ALNS(inputs, initial_vehicles, max_iterations, initial_temperature, learning_rate, cooling_rate, segment_length, sigma1, sigma2, sigma3):
    
    destroy_operators = {
       "random_remove_customers": random_remove_customers
    }
    
    repair_operators = {
       "best_out_of_five_insertion": best_out_of_five_insertion 
    }
    
    destroy_weights = {op: 1 for op in destroy_operators}
    destroy_scores = {op: 0 for op in destroy_operators}
    destroy_usage = {op: 1 for op in destroy_operators}
    
    repair_weights = {op: 1 for op in repair_operators}
    repair_scores = {op: 0 for op in repair_operators}
    repair_usage = {op: 1 for op in repair_operators}
        
    def select_destroy_operator():
        total_weight = sum(destroy_weights.values())
        choices, weights = zip(*destroy_weights.items())
        return random.choices(choices, weights=[w / total_weight for w in weights])[0]
    
    def select_repair_operator():
        total_weight = sum(repair_weights.values())
        choices, weights = zip(*repair_weights.items())
        return random.choices(choices, weights=[w / total_weight for w in weights])[0]
    
    def update_weights():
        for op in destroy_operators:
            destroy_weights[op] = destroy_weights[op] * (1 - learning_rate) + learning_rate * (destroy_scores[op] / destroy_usage[op])
        for op in repair_operators:
            repair_weights[op] = repair_weights[op] * (1 - learning_rate) + learning_rate * (repair_scores[op] / repair_usage[op])
            
    vehicles = {veh: copy.deepcopy(vehicle) for veh, vehicle in initial_vehicles.items()}   
    
    # Initialize the best solution
    objective = compute_objective(vehicles)
    best_objective = objective
    best_vehicles = vehicles
    temperature = initial_temperature
    
    # Track operator weights for visualization
    destroy_weight_history = {op: [] for op in destroy_operators}
    repair_weight_history = {op: [] for op in repair_operators}
    objective_history = [best_objective]
    best_objective_history = [best_objective]
    
    for iteration in range(max_iterations):
        new_vehicles = {veh: copy.deepcopy(vehicle) for veh, vehicle in vehicles.items()} 
        
        destroy_operator = select_destroy_operator()
        print(f"Selected destroy_operator: {destroy_operator}")
        new_vehicles, removed_customers, affected_vehicles = destroy_operators[destroy_operator](new_vehicles, inputs)
        destroy_usage[destroy_operator] += 1
        
        repair_operator = select_repair_operator()
        print(f"Selected repair_operator: {repair_operator}")
        new_vehicles, affected_vehicles = repair_operators[repair_operator](new_vehicles, inputs, removed_customers, affected_vehicles)
        repair_usage[repair_operator] += 1
        
        for vehicle in affected_vehicles:
            new_vehicles[vehicle].unloading_completion_time = determine_unloading_completion_time(vehicles[vehicle],inputs)
            new_vehicles[vehicle].penalty_costs_customer = evaluate_penalty_costs(vehicles[vehicle],inputs)[0]
            new_vehicles[vehicle].penalty_costs_depot = evaluate_penalty_costs(vehicles[vehicle],inputs)[1]
            new_vehicles[vehicle].locker_costs = evaluate_locker_costs(vehicles[vehicle],inputs)
            new_vehicles[vehicle].vehicle_deployment_costs = evaluate_vehicle_deployment_costs(vehicles[vehicle],inputs)
            new_vehicles[vehicle].travel_costs = evaluate_travel_costs(vehicles[vehicle],inputs)
        
        new_objective = compute_objective(new_vehicles)
        
        if check_solution_feasibility_from_dict(new_vehicles, inputs)[0] == 1:
            delta = objective - new_objective
            acceptance_probability = math.exp(delta / temperature) if delta < 0 else 1

            # First, check if the new objective is better (lower for minimization)
            if new_objective < objective:
                # If it's better, update the solution and consider it an improvement
                vehicles = new_vehicles
                objective = new_objective
                # If it's a new best solution, update best_solution
                if new_objective < best_objective:  # Minimization: check if the new objective is lower
                    best_objective = new_objective
                    best_vehicles = new_vehicles
                    destroy_scores[destroy_operator] += sigma1  # Global best found
                    repair_scores[repair_operator] += sigma1 
                    print(f"Iteration {iteration}: New global best found with objective {new_objective:.3f}")
                else:
                    destroy_scores[destroy_operator] += sigma2  
                    repair_scores[repair_operator] += sigma2
                    print(f"Iteration {iteration}: Improved solution with objective {new_objective:.3f}")
            else:
                # If the new solution is worse, accept it based on the acceptance probability
                if random.random() < acceptance_probability:
                    vehicles = new_vehicles
                    objective = new_objective
                    destroy_scores[destroy_operator] += sigma3 
                    repair_scores[repair_operator] += sigma3
                    print(f"Iteration {iteration}: Worse solution accepted with objective {new_objective:.3f}")
                else:
                    print(f"Iteration {iteration}: Worse solution not accepted (probability check failed), objective {new_objective:.3f}")
                    
        else:
            print(f"Iteration {iteration}: Infeasible solution, skipping.")
        
        # Record objectives for visualization
        objective_history.append(new_objective)
        best_objective_history.append(best_objective)
        
        # Record weights for visualization
        for op in destroy_operators:
            destroy_weight_history[op].append(destroy_weights[op])
        for op in repair_operators:
            repair_weight_history[op].append(repair_weights[op])

        if iteration % segment_length == 0 and iteration >= segment_length:
            update_weights()
            destroy_scores = {op: 0 for op in destroy_operators}
            destroy_usage = {op: 1 for op in destroy_operators}
            repair_scores = {op: 0 for op in repair_operators}
            repair_usage = {op: 1 for op in repair_operators}

        temperature *= cooling_rate
        
    # Plotting operator weights
    plt.figure(figsize=(10, 6))
    for op in destroy_operators:
        plt.plot(destroy_weight_history[op], label=op)
    plt.xlabel('Iteration')
    plt.ylabel('Destroy Operator Weights')
    plt.title('Destroy Operator Weights over Iterations')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    plt.figure(figsize=(10, 6))
    for op in repair_operators:
        plt.plot(repair_weight_history[op], label=op)
    plt.xlabel('Iteration')
    plt.ylabel('Repair Operator Weights')
    plt.title('Repair Operator Weights over Iterations')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    
    #Plotting the objective value
    # Create the plot
    plt.figure(figsize=(10, 5))
    plt.plot(objective_history, label="Objective Value", marker="o", linestyle="-")
    plt.plot(best_objective_history, label="Best Objective Value", marker="s", linestyle="--")
    plt.xlabel("Iteration")
    plt.ylabel("Objective Value")
    plt.title("Objective Value Over Iterations")
    plt.legend()
    plt.grid(True)
    plt.show()
    return best_vehicles
    

