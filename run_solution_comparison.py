import subprocess
import sys
import os

# Function to update inputs.py with new parameters for each experiment
def update_inputs(method,schedule_small, clustering_requests, clustering_maximum, subset, max_num_of_ulds_per_R, comp_level,
                  Payload, free_aircraft_placement, r_seed, linearize_PP, w_max, w_min, number_of_iterations,
                  paths_per_request_cap, max_num_paths_per_r, number_of_solutions, number_of_solutions_div, diversification, div_method):
    inputs_content = f"""
# inputs.py

# General settings
method = '{method}'
schedule_small = {schedule_small}
clustering_requests = {clustering_requests}
clustering_maximum = {clustering_maximum}
subset = {subset}
max_num_of_ulds_per_R = {max_num_of_ulds_per_R}
comp_level = '{comp_level}'
Payload = {Payload}
free_aircraft_placement = {free_aircraft_placement}
r_seed = {r_seed}

# RMP_CG_classes.py specific settings
linearize_PP = {linearize_PP}
w_max = {w_max}
w_min = {w_min}
number_of_iterations = {number_of_iterations}
paths_per_request_cap = {paths_per_request_cap}
max_num_paths_per_r = {max_num_paths_per_r}
number_of_solutions = {number_of_solutions}
number_of_solutions_div = {number_of_solutions_div}
diversification = {diversification}
div_method = '{div_method}'  # all or any
"""
    with open('inputs.py', 'w') as f:
        f.write(inputs_content)

# Function to run the main script
def run_comparison():
    subprocess.run([sys.executable, "solution_comparison.py"])

# Here we can specify either CG or SEQ for the method, as we will call both anyway. In fact, our goal is to compare the same 
# instance solved with the integrated model (CG) and the sequential one (SEQ) to highlight similarities and differences
experiments = [
    {
        'method': 'CG', 'schedule_small': False, 'clustering_requests': False, 'clustering_maximum': 1, 'subset': True,
        'max_num_of_ulds_per_R': 15, 'comp_level': 'L', 'Payload': 65, 'free_aircraft_placement': False, 'r_seed': 42,
        'linearize_PP': False, 'w_max': True, 'w_min': False, 'number_of_iterations': 5,
        'paths_per_request_cap': True, 'max_num_paths_per_r': 200, 'number_of_solutions': 20,
        'number_of_solutions_div': 35,
        'diversification': False, 'div_method': 'all'
    },
]

# Define folder where to store all the comparison results for esdier access and processing
cwd = os.getcwd()
comparison_folder_name = "comparison"
if not os.path.exists(os.path.join(cwd,comparison_folder_name)):
    os.makedirs(os.path.join(cwd,comparison_folder_name))

# Run each experiment
for experiment in experiments:
    # Update inputs.py with parameters from the current experiment
    update_inputs(**experiment)

    # Run the main script
    run_comparison()