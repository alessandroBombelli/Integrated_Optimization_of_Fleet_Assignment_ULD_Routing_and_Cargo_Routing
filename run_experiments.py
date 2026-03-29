import subprocess
import sys
import os
from itertools import product

# Function to update inputs.py with new parameters for each experiment
def update_inputs(method, schedule_small, clustering_requests, clustering_maximum, subset, max_num_of_ulds_per_R, comp_level,
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
def run_CG_script():
    subprocess.run([sys.executable, "RMP_CG_classes.py"])

def run_SEQ_script():
    subprocess.run([sys.executable, "sequential_stage2.py"])

def run_AB_script():
    subprocess.run([sys.executable, "arcbased.py"])

# Define different sets of inputs for each experiment
experiments_CG = [
{
        'method': 'CG', 'schedule_small': False, 'clustering_requests': False, 'clustering_maximum': 1, 'subset': True,
        'max_num_of_ulds_per_R': 15, 'comp_level': ['H'], 'Payload': [65,80], 'free_aircraft_placement': False, 'r_seed': 42,
        'linearize_PP': False, 'w_max': True, 'w_min': False, 'number_of_iterations': 25,
        'paths_per_request_cap': True, 'max_num_paths_per_r': 200, 'number_of_solutions': 20,
        'number_of_solutions_div': 35,
        'diversification': False, 'div_method': 'all'
    },
]

expanded_experiments = []

for exp in experiments_CG:
    keys = exp.keys()
    values = [
        v if isinstance(v, list) else [v]
        for v in exp.values()
    ]

    for combo in product(*values):
        expanded_experiments.append(dict(zip(keys, combo)))

experiments_CG = expanded_experiments

experiments_SEQ = [
    {
        'method': 'SEQ', 'schedule_small': False, 'clustering_requests': False, 'clustering_maximum': 1, 'subset': True,
        'max_num_of_ulds_per_R': 15, 'comp_level': 'L', 'Payload': 65, 'free_aircraft_placement': False, 'r_seed': 42,
        'linearize_PP': False, 'w_max': True, 'w_min': False, 'number_of_iterations': 5,
        'paths_per_request_cap': True, 'max_num_paths_per_r': 200, 'number_of_solutions': 20,
        'number_of_solutions_div': 35,
        'diversification': False, 'div_method': 'all'
    },
]

experiments_AB = [
    {
        'method': 'AB', 'schedule_small': True, 'clustering_requests': False, 'clustering_maximum': 0, 'subset': True,
        'max_num_of_ulds_per_R': 50, 'comp_level': 'L', 'Payload': 50, 'free_aircraft_placement': False, 'r_seed': 42,
        'linearize_PP': False, 'w_max': True, 'w_min': False, 'number_of_iterations': 5,
        'paths_per_request_cap': False, 'max_num_paths_per_r': 200, 'number_of_solutions': 20,
        'number_of_solutions_div': 35,
        'diversification': False, 'div_method': 'all'
    },

]

### Creating a folder named "results" that will contain
### pickle files, mostly for comparison of the integrated
### and sequential model, in case such a folder does not
### exist yet
cwd = os.getcwd()
results_folder_name = "results"
if not os.path.exists(os.path.join(cwd,results_folder_name)):
    os.makedirs(os.path.join(cwd,results_folder_name))


for experiment in experiments_CG:
    # Update inputs.py with parameters from the current experiment
    update_inputs(**experiment)

    # Run the main script
    run_CG_script()

# for experiment in experiments_SEQ:
#     # Update inputs.py with parameters from the current experiment
#     update_inputs(**experiment)

#     # Run the main script
#     run_SEQ_script()

# for experiment in experiments_AB:
#     # Update inputs.py with parameters from the current experiment
#     update_inputs(**experiment)

#     # Run the main script
#     run_AB_script()






