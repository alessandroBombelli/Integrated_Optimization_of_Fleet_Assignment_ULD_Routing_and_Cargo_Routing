import pickle
import setsparameters
import inputs
from setsparameters import comp_ULD_check
import numpy as np
from collections import defaultdict
import pandas as pd
import logging
import os

F_dict = setsparameters.F_dict
U_uld_type = setsparameters.U_uld_type
U_v_f = setsparameters.U_v_f
U_dict = setsparameters.U_dict
A_all_dict_2 = setsparameters.A_all_dict_2
F_u = setsparameters.F_u
R_dict = setsparameters.R_dict
K = setsparameters.K
airports_IATA = setsparameters.airports_IATA
V_info = setsparameters.V_info
F_info = setsparameters.F_info
R_u = setsparameters.R_u
W_fk = setsparameters.W_fk
INC_dict_u = setsparameters.INC_dict_u
N_dict_idx_at = setsparameters.N_dict_idx_at
N_dict_at_idx = setsparameters.N_dict_at_idx

name_CG = ""
if inputs.schedule_small:
    name_CG += 'reduced'
if not inputs.schedule_small:
    name_CG +=  'full'
name_CG = name_CG + '_' + inputs.comp_level
name_CG = name_CG + '_' + str(inputs.Payload)
if inputs.free_aircraft_placement:
    name_CG = name_CG + '_free'
if not inputs.free_aircraft_placement:
    name_CG = name_CG + '_restricted'
if inputs.subset:
    name_CG = name_CG + '_subset' + str(inputs.max_num_of_ulds_per_R)
if inputs.clustering_requests:
    if inputs.clustering_maximum == 0:
        name_CG = name_CG + '_clusteringSmall'
    if inputs.clustering_maximum == 1:
        name_CG = name_CG + '_clusteringLarge'
name_CG = name_CG + '_' + str(inputs.number_of_iterations) + 'it'
if inputs.linearize_PP:
    name_CG = name_CG + '_linPP'
if inputs.w_min:
    name_CG = name_CG + '_w_min'
if inputs.w_max:
    name_CG = name_CG + '_w_max'
if inputs.paths_per_request_cap:
    name_CG = name_CG + '_cap' + str(inputs.max_num_paths_per_r)
if inputs.diversification:
    name_CG = name_CG + '_div' + inputs.div_method
name_CG = name_CG + '_seed' + str(inputs.r_seed) + '_CG'

name_SEQ = ""
if inputs.schedule_small:
    name_SEQ = 'reduced'
if not inputs.schedule_small:
    name_SEQ = 'full'
name_SEQ = name_SEQ + '_' + inputs.comp_level
name_SEQ = name_SEQ + '_' + str(inputs.Payload)
if inputs.subset:
    name_SEQ = name_SEQ + '_subset' + str(inputs.max_num_of_ulds_per_R)
if inputs.clustering_requests:
    if inputs.clustering_maximum == 0:
        name_SEQ = name_SEQ + '_clusteringSmall'
    if inputs.clustering_maximum == 1:
        name_SEQ = name_SEQ + '_clusteringLarge'
if inputs.free_aircraft_placement:
    name_SEQ = name_SEQ + '_free'
if not inputs.free_aircraft_placement:
    name_SEQ = name_SEQ + '_restricted'
name_SEQ = name_SEQ + '_seed' + str(inputs.r_seed) + '_SEQ'

name_instance = ""
if inputs.schedule_small:
    name_instance = 'reduced'
if not inputs.schedule_small:
    name_instance = 'full'
name_instance = name_instance + '_' + inputs.comp_level
name_instance = name_instance + '_' + str(inputs.Payload)
if inputs.subset:
    name_instance = name_instance + '_subset' + str(inputs.max_num_of_ulds_per_R)
if inputs.clustering_requests:
    if inputs.clustering_maximum == 0:
        name_instance = name_instance + '_clusteringSmall'
    if inputs.clustering_maximum == 1:
        name_instance = name_instance + '_clusteringLarge'
if inputs.free_aircraft_placement:
    name_instance = name_instance + '_free'
if not inputs.free_aircraft_placement:
    name_instance = name_instance + '_restricted'
name_instance = name_instance + '_seed' + str(inputs.r_seed)

# Specify folder where to store results
cwd = os.getcwd()
instance_folder = os.path.join(cwd,"comparison",name_instance)
os.makedirs(instance_folder, exist_ok=True)

# Specify the file names for the CG model
x_file_name_CG = 'pickle_files/'+name_CG+'/x_data.pkl'
y_file_name_CG = 'pickle_files/'+name_CG+'/y_data.pkl'
z_file_name_CG = 'pickle_files/'+name_CG+'/z_data.pkl'

# Specify the file names for the SEQ model
x_file_name_SEQ_1 = 'pickle_files/'+name_SEQ+'/x_first_stage_data.pkl'
y_file_name_SEQ_1 = 'pickle_files/'+name_SEQ+'/y_first_stage_data.pkl'
z_file_name_SEQ_1 = 'pickle_files/'+name_SEQ+'/z_first_stage_data.pkl'
x_file_name_SEQ_2 = 'pickle_files/'+name_SEQ+'/x_data.pkl'
y_file_name_SEQ_2 = 'pickle_files/'+name_SEQ+'/y_data.pkl'
z_file_name_SEQ_2 = 'pickle_files/'+name_SEQ+'/z_data.pkl'

#################################################################### 
### SAVING GENERAL INPUT FILES THAT ARE COMMON ACROSS ALL MODELS ###
####################################################################
F_dict_file = os.path.join(instance_folder,'F_dict.pkl')
## Write the dictionaries to pickle files
with open(F_dict_file, 'wb') as file:
    pickle.dump(F_dict, file)
R_dict_file = os.path.join(instance_folder,'R_dict.pkl')
## Write the dictionaries to pickle files
with open(R_dict_file, 'wb') as file:
    pickle.dump(R_dict, file)
V_info_file = os.path.join(instance_folder,'V_info.pkl')
## Write the dictionaries to pickle files
with open(V_info_file, 'wb') as file:
    pickle.dump(V_info, file)
F_info_file = os.path.join(instance_folder,'F_info.pkl')
## Write the dictionaries to pickle files
with open(F_info_file, 'wb') as file:
    pickle.dump(F_info, file)
airports_IATA_file = os.path.join(instance_folder,'airports_IATA.pkl')
## Write the dictionaries to pickle files
with open(airports_IATA_file, 'wb') as file:
    pickle.dump(airports_IATA, file)
W_fk_file = os.path.join(instance_folder,'W_fk.pkl')
## Write the dictionaries to pickle files
with open(W_fk_file, 'wb') as file:
    pickle.dump(W_fk, file)
K_file = os.path.join(instance_folder,'K.pkl')
## Write the dictionaries to pickle files
with open(K_file, 'wb') as file:
    pickle.dump(K, file)
N_dict_at_idx_file = os.path.join(instance_folder,'N_dict_at_idx.pkl')
## Write the dictionaries to pickle files
with open(N_dict_at_idx_file, 'wb') as file:
    pickle.dump(N_dict_at_idx, file)
N_dict_idx_at_file = os.path.join(instance_folder,'N_dict_idx_at.pkl')
## Write the dictionaries to pickle files
with open(N_dict_idx_at_file, 'wb') as file:
    pickle.dump(N_dict_idx_at, file)


#############################################
### RETRIEVE SOLUTION OF INTEGRATED MODEL ###
#############################################
p_file_name = 'pickle_files/'+name_CG+'/P_dict.pkl'

with open(p_file_name, "rb") as file:
    P_dict = pickle.load(file)
    C_up = pickle.load(file)
    R_up = pickle.load(file)
    W_up = pickle.load(file)
    paths_per_it_dict = pickle.load(file)
    elapsed_time_global = pickle.load(file)

print('Numer of paths:',len(P_dict.keys()))
print('CG time:', elapsed_time_global)
print(paths_per_it_dict)

logging.info(f'Numer of paths: {len(P_dict.keys())}')
logging.info(f'CG time: {elapsed_time_global}')
logging.info(paths_per_it_dict)

with open(x_file_name_CG, "rb") as file:
    x_dict = pickle.load(file)

with open(y_file_name_CG, "rb") as file:
    y_dict = pickle.load(file)
    PATH_uld_routing_costs = pickle.load(file)

with open(z_file_name_CG, "rb") as file:
    z_dict = pickle.load(file)
    PATH_revenue = pickle.load(file)

weight_counter = defaultdict(int)
volume_counter = defaultdict(int)

logging.info(V_info)

uld_lf = []
uld_vf = []

F_CG_info_dict = {} # Dictionary where we store which aircraft type is flying flight arc f

for u in U_dict.keys():
    if U_dict[u][2] in (0, 1):
        uld_weight = 1.5
        uld_volume = 4.5
    elif U_dict[u][2] in (2, 3):
        uld_weight = 4.6
        uld_volume = 10.7
    for r in R_dict.keys():
        value = z_dict.get((r, u))
        if value:
            weight_counter[u] += R_dict[r][5]
            volume_counter[u] += R_dict[r][6]
    if weight_counter[u] > 0:
        uld_lf.append(weight_counter[u] / uld_weight)
        uld_vf.append(volume_counter[u] / uld_volume)
F_plr_lf = {}
flight_costs = 0
ULDs_on_flight = {}
R_on_f = {}
R_on_f_full_info = {}
for f in F_dict.keys():
    ULDs_on_flight[f] = []
    found = False  # To track if any k exists for the current f
    for k in K.keys():
        if x_dict.get((f, k)) is not None and x_dict.get((f, k)) >= 0.9:

            LD3_count = 0
            LD7_count = 0
            weight = 0

            for u in U_dict.keys():
                if y_dict.get((f,u)) is not None and y_dict.get((f, u)) >= 0.9:
                    ULDs_on_flight[f].append(u)
                    if U_dict[u][2] in (0, 1):
                        LD3_count += 1
                    if U_dict[u][2] in (2, 3):
                        LD7_count += 1

            R_on_f[f] = [r for r in R_dict.keys() for u in ULDs_on_flight[f] if
                             z_dict.get((r, u)) is not None and z_dict.get((r, u)) >= 0.9]
            for r in R_on_f[f]:
                weight += R_dict[r][5]

            F_plr_lf[f] = weight / W_fk[(f, k)]
            R_on_f_full_info[f] = {'requests':[r for r in R_dict.keys() for u in ULDs_on_flight[f] if
                             z_dict.get((r, u)) is not None and z_dict.get((r, u)) >= 0.9],
                             'weight':weight,
                             'max_weight':W_fk[(f, k)]}

            print(f'Flight arc {f} is being flown by aircraft type {k} and '
                  f'has {LD3_count} LD3 units and {LD7_count} LD7 units,'
                  f'and a payload range based load factor of {F_plr_lf[f]}')
            logging.info(f'Flight arc {f} is being flown by aircraft type {k} and '
                  f'has {LD3_count} LD3 units and {LD7_count} LD7 units,'
                  f'and a payload range based load factor of {F_plr_lf[f]}')

            flight_costs -= K[k]['OC'] * F_info[f]['distance']
            found = True

            F_CG_info_dict[f] = {'Aircraft type':k,'Payload':weight,'Load Factor':F_plr_lf[f]}

    if not found:
        print(f'FLIGHT ARC {f} IS NOT BEING FLOWN BY ANY AIRCRAFT TYPE')
        logging.info(f'FLIGHT ARC {f} IS NOT BEING FLOWN BY ANY AIRCRAFT TYPE')

# Convert dictionary to DataFrame
df = pd.DataFrame.from_dict(F_CG_info_dict, orient='index', columns=['Aircraft type','Payload','Load Factor'])
# Reset index so the keys become a proper column
df.reset_index(inplace=True)
# Rename index column to 'Key'
df.rename(columns={'index': 'Flight Arc'}, inplace=True)
# Display the DataFrame
print(df)

R_transported = [r for r in R_dict.keys() for u in U_dict.keys() if z_dict.get((r,u)) is not None and z_dict.get((r, u)) >= 0.9]
R_transported_ratio = len(R_transported)/len(R_dict)*100
R_OD = {(o,d):[r for r,v in R_dict.items() if v[0]==o and v[1]==d] for o in airports_IATA for d in airports_IATA if d!=o}
R_OD_transported = {od:[req for req in R_OD[od]
                        if req in R_transported]
                    for od in R_OD.keys()}
R_OD_unfulfilled = {od:[req for req in R_OD[od]
                        if req not in R_transported]
                    for od in R_OD.keys()}
R_OD_ratio = {od: np.round(len(R_OD_transported[od])/len(R_OD[od])*100,1) if
              len(R_OD[od]) > 0 else -1
                    for od in R_OD.keys()}

R_unfulfilled = [r for r in R_dict if r not in R_transported]
combined_weight =0
for r in R_transported:
     combined_weight += R_dict[r][5]
revenue = 0

##########################################################
### Note: average revenue hard-coded. A bit dangerous! ###
### To be fixed                                        ###
##########################################################
for r in R_transported:
    revenue += R_dict[r][5] * R_dict[r][7] * 4000
print(f'Percentage of transported requests: {R_transported_ratio}')
print(f'Revenue of transported requests: {revenue}')

lost_revenue = 0
for r in R_unfulfilled:
    lost_revenue += R_dict[r][5] * R_dict[r][7] * 4000
average_rev_transported = revenue/len(R_transported)
average_rev_unfulfilled = lost_revenue/len(R_unfulfilled)

R_no_feature_transported  = [idx for idx in R_transported if R_dict[idx][8] == 0 and R_dict[idx][9] == 0]
R_hazfeature_transported  = [idx for idx in R_transported if R_dict[idx][8] == 1 and R_dict[idx][9] == 0]
R_tempfeature_transported = [idx for idx in R_transported if R_dict[idx][9] == 1 and R_dict[idx][8] == 0]
R_bothfeature_transported = [idx for idx in R_transported if R_dict[idx][8] == 1 and R_dict[idx][9] == 1]

total_chemical_count = sum(1 for key, value in R_dict.items() if value[4] == 'chemical')
transported_chemical_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'chemical')
percentage_chemical = transported_chemical_count / total_chemical_count
print(f'Percentage of chemical requests transported: {percentage_chemical}')

total_perishable_count = sum(1 for key, value in R_dict.items() if value[4] == 'perishable')
transported_perishable_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'perishable')
percentage_perishable = transported_perishable_count / total_perishable_count
print(f'Percentage of perishable requests transported: {percentage_perishable}')

total_heavy_count = sum(1 for key, value in R_dict.items() if value[4] == 'heavy')
transported_heavy_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'heavy')
percentage_heavy = transported_heavy_count / total_heavy_count
print(f'Percentage of heavy requests transported: {percentage_heavy}')

total_other_count = sum(1 for key, value in R_dict.items() if value[4] == 'other')
transported_other_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'other')
percentage_other = transported_other_count / total_other_count
print(f'Percentage of other requests transported: {percentage_other}')

ULDs_on_arc = {}
ULDs_OD = {}
ULD_used = []
# Iterate through the original dictionary
for (arc, u), value in y_dict.items():
    # If the arc is not already in the dictionary, add it with an empty list
    if arc not in ULDs_on_arc:
        ULDs_on_arc[arc] = []
    # Append the ULD to the list of ULDs for this arc
    ULDs_on_arc[arc].append(u)
    if (U_dict[u][0][0][0], U_dict[u][0][1][0]) not in ULDs_OD:
        ULDs_OD[(U_dict[u][0][0][0], U_dict[u][0][1][0])] = []
    if u not in ULDs_OD[(U_dict[u][0][0][0], U_dict[u][0][1][0])]:
        ULDs_OD[(U_dict[u][0][0][0], U_dict[u][0][1][0])].append(u)
    if u not in ULD_used:
        ULD_used.append(u)
ratio_ULD_used = len(ULD_used)/len(U_dict) * 100
U_uld_type_used   = {k:[idx for idx in ULD_used if U_dict[idx][2] ==k] for k in V_info}

Requests_in_ULD = {}
for (r, u), value in z_dict.items():
    # If the arc is not already in the dictionary, add it with an empty list
    if u not in Requests_in_ULD:
        Requests_in_ULD[u] = []
    # Append the ULD to the list of ULDs for this arc
    Requests_in_ULD[u].append(r)

R_in_too_advanced_ULD = []
for u in U_uld_type_used[1]:
    if u in Requests_in_ULD.keys():
        for r in R_no_feature_transported:
            if r in Requests_in_ULD[u]:
                R_in_too_advanced_ULD.append(r)



for u in U_uld_type_used[3]:
    if u in Requests_in_ULD.keys():
        for r in R_no_feature_transported:
            if r in Requests_in_ULD[u]:
                R_in_too_advanced_ULD.append(r)

R_nofeature_advancedULD_ratio = len(R_in_too_advanced_ULD)/len(R_no_feature_transported) * 100 if len(R_no_feature_transported) > 0 else -1

average_uld_unit_cost = (len(U_uld_type_used[0]) * 0.105 + len(U_uld_type_used[1]) * 0.115 + len(U_uld_type_used[2]) * 0.1 + len(U_uld_type_used[3]) * 0.135 )/ len(ULD_used)

uld_routing_costs = 0
for f in F_dict.keys():
    ULDs_to_try = ULDs_on_arc.get(f)
    if ULDs_to_try == None:
        continue
    for u in ULDs_to_try:
        uld_type = U_dict[u][2]
        uld_routing_costs -= V_info[uld_type][5] * F_info[f]['distance']

print(f'Revenue with transported requests: {revenue}')
logging.info(f'Revenue with transported requests: {revenue}')


print(f'Path based revenue: {PATH_revenue}')
logging.info(f'Path based revenue: {PATH_revenue}')

print(f'Costs of the flights operated: {flight_costs}')
print(f'Costs of routing the ULDs {uld_routing_costs}')

logging.info(f'Costs of the flights operated: {flight_costs}')
logging.info(f'Costs of routing the ULDs {uld_routing_costs}')


print(f'Path based ULD routing costs: {PATH_uld_routing_costs}')
logging.info(f'Path based ULD routing costs: {PATH_uld_routing_costs}')

CG_solution = {}
CG_solution['Profit'] = revenue+flight_costs+uld_routing_costs
CG_solution['Revenue'] = revenue
CG_solution['Fleet_op_cost'] = flight_costs
CG_solution['ULD_op_cost'] = uld_routing_costs
CG_solution['R_f'] = R_on_f_full_info
CG_solution['F_CG_info_dict'] = F_CG_info_dict


CG_solution_file = os.path.join(instance_folder,'CG_solution.pkl')
## Write the dictionaries to pickle files
with open(CG_solution_file, 'wb') as file:
    pickle.dump(CG_solution, file)

##########################################################
### RETRIEVE SOLUTION OF SEQUENTIAL MODEL: FIRST STAGE ###
##########################################################

with open(x_file_name_SEQ_1, "rb") as file:
    x_dict = pickle.load(file)

with open(y_file_name_SEQ_1, "rb") as file:
    y_dict = pickle.load(file)

with open(z_file_name_SEQ_1, "rb") as file:
    z_dict = pickle.load(file)

weight_counter = defaultdict(int)
volume_counter = defaultdict(int)

logging.info(V_info)

uld_lf = []
uld_vf = []

F_SEQ1_info_dict = {} # Dictionary where we store which aircraft type is flying flight arc f

for u in U_dict.keys():
    if U_dict[u][2] in (0, 1):
        uld_weight = 1.5
        uld_volume = 4.5
    elif U_dict[u][2] in (2, 3):
        uld_weight = 4.6
        uld_volume = 10.7
    for r in R_dict.keys():
        value = z_dict.get((r, u))
        if value:
            weight_counter[u] += R_dict[r][5]
            volume_counter[u] += R_dict[r][6]
    if weight_counter[u] > 0:
        uld_lf.append(weight_counter[u] / uld_weight)
        uld_vf.append(volume_counter[u] / uld_volume)
F_plr_lf = {}
flight_costs = 0
ULDs_on_flight = {}
R_on_f = {}
R_on_f_full_info = {}
for f in F_dict.keys():
    ULDs_on_flight[f] = []
    found = False  # To track if any k exists for the current f
    for k in K.keys():
        if x_dict.get((f, k)) is not None and x_dict.get((f, k)) >= 0.9:

            LD3_count = 0
            LD7_count = 0
            weight = 0

            for u in U_dict.keys():
                if y_dict.get((f,u)) is not None and y_dict.get((f, u)) >= 0.9:
                    ULDs_on_flight[f].append(u)
                    if U_dict[u][2] in (0, 1):
                        LD3_count += 1
                    if U_dict[u][2] in (2, 3):
                        LD7_count += 1

            R_on_f[f] = [r for r in R_dict.keys() for u in ULDs_on_flight[f] if
                             z_dict.get((r, u)) is not None and z_dict.get((r, u)) >= 0.9]
            for r in R_on_f[f]:
                weight += R_dict[r][5]

            F_plr_lf[f] = weight / W_fk[(f, k)]
            R_on_f_full_info[f] = {'requests':[r for r in R_dict.keys() for u in ULDs_on_flight[f] if
                             z_dict.get((r, u)) is not None and z_dict.get((r, u)) >= 0.9],
                             'weight':weight,
                             'max_weight':W_fk[(f, k)]}

            print(f'Flight arc {f} is being flown by aircraft type {k} and '
                  f'has {LD3_count} LD3 units and {LD7_count} LD7 units,'
                  f'and a payload range based load factor of {F_plr_lf[f]}')
            logging.info(f'Flight arc {f} is being flown by aircraft type {k} and '
                  f'has {LD3_count} LD3 units and {LD7_count} LD7 units,'
                  f'and a payload range based load factor of {F_plr_lf[f]}')

            flight_costs -= K[k]['OC'] * F_info[f]['distance']
            found = True

            F_SEQ1_info_dict[f] = {'Aircraft type':k,'Payload':weight,'Load Factor':F_plr_lf[f]}

    if not found:
        print(f'FLIGHT ARC {f} IS NOT BEING FLOWN BY ANY AIRCRAFT TYPE')
        logging.info(f'FLIGHT ARC {f} IS NOT BEING FLOWN BY ANY AIRCRAFT TYPE')

# Convert dictionary to DataFrame
df = pd.DataFrame.from_dict(F_SEQ1_info_dict, orient='index', columns=['Aircraft type','Payload','Load Factor'])
# Reset index so the keys become a proper column
df.reset_index(inplace=True)
# Rename index column to 'Key'
df.rename(columns={'index': 'Flight Arc'}, inplace=True)
# Display the DataFrame
print(df)

R_transported = [r for r in R_dict.keys() for u in U_dict.keys() if z_dict.get((r,u)) is not None and z_dict.get((r, u)) >= 0.9]
R_transported_ratio = len(R_transported)/len(R_dict)*100
R_OD = {(o,d):[r for r,v in R_dict.items() if v[0]==o and v[1]==d] for o in airports_IATA for d in airports_IATA if d!=o}
R_OD_transported = {od:[req for req in R_OD[od]
                        if req in R_transported]
                    for od in R_OD.keys()}
R_OD_unfulfilled = {od:[req for req in R_OD[od]
                        if req not in R_transported]
                    for od in R_OD.keys()}
R_OD_ratio = {od: np.round(len(R_OD_transported[od])/len(R_OD[od])*100,1) if
              len(R_OD[od]) > 0 else -1
                    for od in R_OD.keys()}

R_unfulfilled = [r for r in R_dict if r not in R_transported]
combined_weight =0
for r in R_transported:
     combined_weight += R_dict[r][5]
revenue = 0

##########################################################
### Note: average revenue hard-coded. A bit dangerous! ###
### To be fixed                                        ###
##########################################################
for r in R_transported:
    revenue += R_dict[r][5] * R_dict[r][7] * 4000
print(f'Percentage of transported requests: {R_transported_ratio}')
print(f'Revenue of transported requests: {revenue}')

lost_revenue = 0
for r in R_unfulfilled:
    lost_revenue += R_dict[r][5] * R_dict[r][7] * 4000
average_rev_transported = revenue/len(R_transported)
average_rev_unfulfilled = lost_revenue/len(R_unfulfilled)

R_no_feature_transported  = [idx for idx in R_transported if R_dict[idx][8] == 0 and R_dict[idx][9] == 0]
R_hazfeature_transported  = [idx for idx in R_transported if R_dict[idx][8] == 1 and R_dict[idx][9] == 0]
R_tempfeature_transported = [idx for idx in R_transported if R_dict[idx][9] == 1 and R_dict[idx][8] == 0]
R_bothfeature_transported = [idx for idx in R_transported if R_dict[idx][8] == 1 and R_dict[idx][9] == 1]

total_chemical_count = sum(1 for key, value in R_dict.items() if value[4] == 'chemical')
transported_chemical_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'chemical')
percentage_chemical = transported_chemical_count / total_chemical_count
print(f'Percentage of chemical requests transported: {percentage_chemical}')

total_perishable_count = sum(1 for key, value in R_dict.items() if value[4] == 'perishable')
transported_perishable_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'perishable')
percentage_perishable = transported_perishable_count / total_perishable_count
print(f'Percentage of perishable requests transported: {percentage_perishable}')

total_heavy_count = sum(1 for key, value in R_dict.items() if value[4] == 'heavy')
transported_heavy_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'heavy')
percentage_heavy = transported_heavy_count / total_heavy_count
print(f'Percentage of heavy requests transported: {percentage_heavy}')

total_other_count = sum(1 for key, value in R_dict.items() if value[4] == 'other')
transported_other_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'other')
percentage_other = transported_other_count / total_other_count
print(f'Percentage of other requests transported: {percentage_other}')

ULDs_on_arc = {}
ULDs_OD = {}
ULD_used = []
# Iterate through the original dictionary
for (arc, u), value in y_dict.items():
    # If the arc is not already in the dictionary, add it with an empty list
    if arc not in ULDs_on_arc:
        ULDs_on_arc[arc] = []
    # Append the ULD to the list of ULDs for this arc
    ULDs_on_arc[arc].append(u)
    if (U_dict[u][0][0][0], U_dict[u][0][1][0]) not in ULDs_OD:
        ULDs_OD[(U_dict[u][0][0][0], U_dict[u][0][1][0])] = []
    if u not in ULDs_OD[(U_dict[u][0][0][0], U_dict[u][0][1][0])]:
        ULDs_OD[(U_dict[u][0][0][0], U_dict[u][0][1][0])].append(u)
    if u not in ULD_used:
        ULD_used.append(u)
ratio_ULD_used = len(ULD_used)/len(U_dict) * 100
U_uld_type_used   = {k:[idx for idx in ULD_used if U_dict[idx][2] ==k] for k in V_info}

Requests_in_ULD = {}
for (r, u), value in z_dict.items():
    # If the arc is not already in the dictionary, add it with an empty list
    if u not in Requests_in_ULD:
        Requests_in_ULD[u] = []
    # Append the ULD to the list of ULDs for this arc
    Requests_in_ULD[u].append(r)

R_in_too_advanced_ULD = []
for u in U_uld_type_used[1]:
    if u in Requests_in_ULD.keys():
        for r in R_no_feature_transported:
            if r in Requests_in_ULD[u]:
                R_in_too_advanced_ULD.append(r)



for u in U_uld_type_used[3]:
    if u in Requests_in_ULD.keys():
        for r in R_no_feature_transported:
            if r in Requests_in_ULD[u]:
                R_in_too_advanced_ULD.append(r)

R_nofeature_advancedULD_ratio = len(R_in_too_advanced_ULD)/len(R_no_feature_transported) * 100 if len(R_no_feature_transported) > 0 else -1

average_uld_unit_cost = (len(U_uld_type_used[0]) * 0.105 + len(U_uld_type_used[1]) * 0.115 + len(U_uld_type_used[2]) * 0.1 + len(U_uld_type_used[3]) * 0.135 )/ len(ULD_used)

print(f'Revenue with transported requests: {revenue}')
logging.info(f'Revenue with transported requests: {revenue}')


print(f'Path based revenue: {PATH_revenue}')
logging.info(f'Path based revenue: {PATH_revenue}')

print(f'Costs of the flights operated: {flight_costs}')
print(f'Costs of routing the ULDs {uld_routing_costs}')

logging.info(f'Costs of the flights operated: {flight_costs}')
logging.info(f'Costs of routing the ULDs {uld_routing_costs}')

SEQ1_solution = {}
SEQ1_solution['Profit'] = revenue+flight_costs+uld_routing_costs
SEQ1_solution['Revenue'] = revenue
SEQ1_solution['Fleet_op_cost'] = flight_costs
SEQ1_solution['R_f'] = R_on_f_full_info
SEQ1_solution['F_SEQ1_info_dict'] = F_SEQ1_info_dict


SEQ1_solution_file = os.path.join(instance_folder,'SEQ1_solution.pkl')
## Write the dictionaries to pickle files
with open(SEQ1_solution_file, 'wb') as file:
    pickle.dump(SEQ1_solution, file)

###########################################################
### RETRIEVE SOLUTION OF SEQUENTIAL MODEL: SECOND STAGE ###
###########################################################

with open(x_file_name_SEQ_2, "rb") as file:
    x_dict = pickle.load(file)

with open(y_file_name_SEQ_2, "rb") as file:
    y_dict = pickle.load(file)

with open(z_file_name_SEQ_2, "rb") as file:
    z_dict = pickle.load(file)

weight_counter = defaultdict(int)
volume_counter = defaultdict(int)

logging.info(V_info)

uld_lf = []
uld_vf = []

F_SEQ2_info_dict = {} # Dictionary where we store which aircraft type is flying flight arc f

for u in U_dict.keys():
    if U_dict[u][2] in (0, 1):
        uld_weight = 1.5
        uld_volume = 4.5
    elif U_dict[u][2] in (2, 3):
        uld_weight = 4.6
        uld_volume = 10.7
    for r in R_dict.keys():
        value = z_dict.get((r, u))
        if value:
            weight_counter[u] += R_dict[r][5]
            volume_counter[u] += R_dict[r][6]
    if weight_counter[u] > 0:
        uld_lf.append(weight_counter[u] / uld_weight)
        uld_vf.append(volume_counter[u] / uld_volume)
F_plr_lf = {}
flight_costs = 0
ULDs_on_flight = {}
R_on_f = {}
R_on_f_full_info = {}
for f in F_dict.keys():
    ULDs_on_flight[f] = []
    found = False  # To track if any k exists for the current f
    for k in K.keys():
        if x_dict.get((f, k)) is not None and x_dict.get((f, k)) >= 0.9:

            LD3_count = 0
            LD7_count = 0
            weight = 0

            for u in U_dict.keys():
                if y_dict.get((f,u)) is not None and y_dict.get((f, u)) >= 0.9:
                    ULDs_on_flight[f].append(u)
                    if U_dict[u][2] in (0, 1):
                        LD3_count += 1
                    if U_dict[u][2] in (2, 3):
                        LD7_count += 1

            R_on_f[f] = [r for r in R_dict.keys() for u in ULDs_on_flight[f] if
                             z_dict.get((r, u)) is not None and z_dict.get((r, u)) >= 0.9]
            for r in R_on_f[f]:
                weight += R_dict[r][5]

            F_plr_lf[f] = weight / W_fk[(f, k)]
            R_on_f_full_info[f] = {'requests':[r for r in R_dict.keys() for u in ULDs_on_flight[f] if
                             z_dict.get((r, u)) is not None and z_dict.get((r, u)) >= 0.9],
                             'weight':weight,
                             'max_weight':W_fk[(f, k)]}

            print(f'Flight arc {f} is being flown by aircraft type {k} and '
                  f'has {LD3_count} LD3 units and {LD7_count} LD7 units,'
                  f'and a payload range based load factor of {F_plr_lf[f]}')
            logging.info(f'Flight arc {f} is being flown by aircraft type {k} and '
                  f'has {LD3_count} LD3 units and {LD7_count} LD7 units,'
                  f'and a payload range based load factor of {F_plr_lf[f]}')

            flight_costs -= K[k]['OC'] * F_info[f]['distance']
            found = True

            F_SEQ2_info_dict[f] = {'Aircraft type':k,'Payload':weight,'Load Factor':F_plr_lf[f]}

    if not found:
        print(f'FLIGHT ARC {f} IS NOT BEING FLOWN BY ANY AIRCRAFT TYPE')
        logging.info(f'FLIGHT ARC {f} IS NOT BEING FLOWN BY ANY AIRCRAFT TYPE')

# Convert dictionary to DataFrame
df = pd.DataFrame.from_dict(F_SEQ2_info_dict, orient='index', columns=['Aircraft type','Payload','Load Factor'])
# Reset index so the keys become a proper column
df.reset_index(inplace=True)
# Rename index column to 'Key'
df.rename(columns={'index': 'Flight Arc'}, inplace=True)
# Display the DataFrame
print(df)

R_transported = [r for r in R_dict.keys() for u in U_dict.keys() if z_dict.get((r,u)) is not None and z_dict.get((r, u)) >= 0.9]
R_transported_ratio = len(R_transported)/len(R_dict)*100
R_OD = {(o,d):[r for r,v in R_dict.items() if v[0]==o and v[1]==d] for o in airports_IATA for d in airports_IATA if d!=o}
R_OD_transported = {od:[req for req in R_OD[od]
                        if req in R_transported]
                    for od in R_OD.keys()}
R_OD_unfulfilled = {od:[req for req in R_OD[od]
                        if req not in R_transported]
                    for od in R_OD.keys()}
R_OD_ratio = {od: np.round(len(R_OD_transported[od])/len(R_OD[od])*100,1) if
              len(R_OD[od]) > 0 else -1
                    for od in R_OD.keys()}

R_unfulfilled = [r for r in R_dict if r not in R_transported]
combined_weight =0
for r in R_transported:
     combined_weight += R_dict[r][5]
revenue = 0

##########################################################
### Note: average revenue hard-coded. A bit dangerous! ###
### To be fixed                                        ###
##########################################################
for r in R_transported:
    revenue += R_dict[r][5] * R_dict[r][7] * 4000
print(f'Percentage of transported requests: {R_transported_ratio}')
print(f'Revenue of transported requests: {revenue}')

lost_revenue = 0
for r in R_unfulfilled:
    lost_revenue += R_dict[r][5] * R_dict[r][7] * 4000
average_rev_transported = revenue/len(R_transported)
average_rev_unfulfilled = lost_revenue/len(R_unfulfilled)

R_no_feature_transported  = [idx for idx in R_transported if R_dict[idx][8] == 0 and R_dict[idx][9] == 0]
R_hazfeature_transported  = [idx for idx in R_transported if R_dict[idx][8] == 1 and R_dict[idx][9] == 0]
R_tempfeature_transported = [idx for idx in R_transported if R_dict[idx][9] == 1 and R_dict[idx][8] == 0]
R_bothfeature_transported = [idx for idx in R_transported if R_dict[idx][8] == 1 and R_dict[idx][9] == 1]

total_chemical_count = sum(1 for key, value in R_dict.items() if value[4] == 'chemical')
transported_chemical_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'chemical')
percentage_chemical = transported_chemical_count / total_chemical_count
print(f'Percentage of chemical requests transported: {percentage_chemical}')

total_perishable_count = sum(1 for key, value in R_dict.items() if value[4] == 'perishable')
transported_perishable_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'perishable')
percentage_perishable = transported_perishable_count / total_perishable_count
print(f'Percentage of perishable requests transported: {percentage_perishable}')

total_heavy_count = sum(1 for key, value in R_dict.items() if value[4] == 'heavy')
transported_heavy_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'heavy')
percentage_heavy = transported_heavy_count / total_heavy_count
print(f'Percentage of heavy requests transported: {percentage_heavy}')

total_other_count = sum(1 for key, value in R_dict.items() if value[4] == 'other')
transported_other_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'other')
percentage_other = transported_other_count / total_other_count
print(f'Percentage of other requests transported: {percentage_other}')

ULDs_on_arc = {}
ULDs_OD = {}
ULD_used = []
# Iterate through the original dictionary
for (arc, u), value in y_dict.items():
    # If the arc is not already in the dictionary, add it with an empty list
    if arc not in ULDs_on_arc:
        ULDs_on_arc[arc] = []
    # Append the ULD to the list of ULDs for this arc
    ULDs_on_arc[arc].append(u)
    if (U_dict[u][0][0][0], U_dict[u][0][1][0]) not in ULDs_OD:
        ULDs_OD[(U_dict[u][0][0][0], U_dict[u][0][1][0])] = []
    if u not in ULDs_OD[(U_dict[u][0][0][0], U_dict[u][0][1][0])]:
        ULDs_OD[(U_dict[u][0][0][0], U_dict[u][0][1][0])].append(u)
    if u not in ULD_used:
        ULD_used.append(u)
ratio_ULD_used = len(ULD_used)/len(U_dict) * 100
U_uld_type_used   = {k:[idx for idx in ULD_used if U_dict[idx][2] ==k] for k in V_info}

Requests_in_ULD = {}
for (r, u), value in z_dict.items():
    # If the arc is not already in the dictionary, add it with an empty list
    if u not in Requests_in_ULD:
        Requests_in_ULD[u] = []
    # Append the ULD to the list of ULDs for this arc
    Requests_in_ULD[u].append(r)

R_in_too_advanced_ULD = []
for u in U_uld_type_used[1]:
    if u in Requests_in_ULD.keys():
        for r in R_no_feature_transported:
            if r in Requests_in_ULD[u]:
                R_in_too_advanced_ULD.append(r)



for u in U_uld_type_used[3]:
    if u in Requests_in_ULD.keys():
        for r in R_no_feature_transported:
            if r in Requests_in_ULD[u]:
                R_in_too_advanced_ULD.append(r)

R_nofeature_advancedULD_ratio = len(R_in_too_advanced_ULD)/len(R_no_feature_transported) * 100 if len(R_no_feature_transported) > 0 else -1

average_uld_unit_cost = (len(U_uld_type_used[0]) * 0.105 + len(U_uld_type_used[1]) * 0.115 + len(U_uld_type_used[2]) * 0.1 + len(U_uld_type_used[3]) * 0.135 )/ len(ULD_used)

uld_routing_costs = 0
for f in F_dict.keys():
    ULDs_to_try = ULDs_on_arc.get(f)
    if ULDs_to_try == None:
        continue
    for u in ULDs_to_try:
        uld_type = U_dict[u][2]
        uld_routing_costs -= V_info[uld_type][5] * F_info[f]['distance']

print(f'Revenue with transported requests: {revenue}')
logging.info(f'Revenue with transported requests: {revenue}')


print(f'Path based revenue: {PATH_revenue}')
logging.info(f'Path based revenue: {PATH_revenue}')

print(f'Costs of the flights operated: {flight_costs}')
print(f'Costs of routing the ULDs {uld_routing_costs}')

logging.info(f'Costs of the flights operated: {flight_costs}')
logging.info(f'Costs of routing the ULDs {uld_routing_costs}')

SEQ2_solution = {}
SEQ2_solution['Profit'] = revenue+flight_costs+uld_routing_costs
SEQ2_solution['Revenue'] = revenue
SEQ2_solution['Fleet_op_cost'] = flight_costs
SEQ2_solution['ULD_op_cost'] = uld_routing_costs
SEQ2_solution['R_f'] = R_on_f_full_info
SEQ2_solution['F_SEQ2_info_dict'] = F_SEQ2_info_dict


SEQ2_solution_file = os.path.join(instance_folder,'SEQ2_solution.pkl')
## Write the dictionaries to pickle files
with open(SEQ2_solution_file, 'wb') as file:
    pickle.dump(SEQ2_solution, file)

fixed_routing_folder = os.path.join(cwd,"pickle_files",name_SEQ,"results_with_partially_fixed_routing")

if os.path.isdir(fixed_routing_folder):
    print("Analyze SEQ model with partially fixed routing as well")
    # Specify the file names for the SEQ model
    x_file_name_SEQ_1_fixed = os.path.join(fixed_routing_folder,"x_first_stage_data.pkl")
    y_file_name_SEQ_1_fixed = os.path.join(fixed_routing_folder,"y_first_stage_data.pkl")
    z_file_name_SEQ_1_fixed = os.path.join(fixed_routing_folder,"z_first_stage_data.pkl")
    x_file_name_SEQ_2_fixed = os.path.join(fixed_routing_folder,"x_data.pkl")
    y_file_name_SEQ_2_fixed = os.path.join(fixed_routing_folder,"y_data.pkl")
    z_file_name_SEQ_2_fixed = os.path.join(fixed_routing_folder,"z_data.pkl")

    #######################################################################################
    ### RETRIEVE SOLUTION OF SEQUENTIAL MODEL WITH PARTIALLY FIXED ROUTING: FIRST STAGE ###
    #######################################################################################

    with open(x_file_name_SEQ_1_fixed, "rb") as file:
        x_dict = pickle.load(file)

    with open(y_file_name_SEQ_1_fixed, "rb") as file:
        y_dict = pickle.load(file)

    with open(z_file_name_SEQ_1_fixed, "rb") as file:
        z_dict = pickle.load(file)

    weight_counter = defaultdict(int)
    volume_counter = defaultdict(int)

    logging.info(V_info)

    uld_lf = []
    uld_vf = []

    F_SEQ1_fixed_info_dict = {} # Dictionary where we store which aircraft type is flying flight arc f

    for u in U_dict.keys():
        if U_dict[u][2] in (0, 1):
            uld_weight = 1.5
            uld_volume = 4.5
        elif U_dict[u][2] in (2, 3):
            uld_weight = 4.6
            uld_volume = 10.7
        for r in R_dict.keys():
            value = z_dict.get((r, u))
            if value:
                weight_counter[u] += R_dict[r][5]
                volume_counter[u] += R_dict[r][6]
        if weight_counter[u] > 0:
            uld_lf.append(weight_counter[u] / uld_weight)
            uld_vf.append(volume_counter[u] / uld_volume)
    F_plr_lf = {}
    flight_costs = 0
    ULDs_on_flight = {}
    R_on_f = {}
    R_on_f_full_info = {}
    for f in F_dict.keys():
        ULDs_on_flight[f] = []
        found = False  # To track if any k exists for the current f
        for k in K.keys():
            if x_dict.get((f, k)) is not None and x_dict.get((f, k)) >= 0.9:

                LD3_count = 0
                LD7_count = 0
                weight = 0

                for u in U_dict.keys():
                    if y_dict.get((f,u)) is not None and y_dict.get((f, u)) >= 0.9:
                        ULDs_on_flight[f].append(u)
                        if U_dict[u][2] in (0, 1):
                            LD3_count += 1
                        if U_dict[u][2] in (2, 3):
                            LD7_count += 1

                R_on_f[f] = [r for r in R_dict.keys() for u in ULDs_on_flight[f] if
                                z_dict.get((r, u)) is not None and z_dict.get((r, u)) >= 0.9]
                for r in R_on_f[f]:
                    weight += R_dict[r][5]

                F_plr_lf[f] = weight / W_fk[(f, k)]
                R_on_f_full_info[f] = {'requests':[r for r in R_dict.keys() for u in ULDs_on_flight[f] if
                                z_dict.get((r, u)) is not None and z_dict.get((r, u)) >= 0.9],
                                'weight':weight,
                                'max_weight':W_fk[(f, k)]}

                print(f'Flight arc {f} is being flown by aircraft type {k} and '
                    f'has {LD3_count} LD3 units and {LD7_count} LD7 units,'
                    f'and a payload range based load factor of {F_plr_lf[f]}')
                logging.info(f'Flight arc {f} is being flown by aircraft type {k} and '
                    f'has {LD3_count} LD3 units and {LD7_count} LD7 units,'
                    f'and a payload range based load factor of {F_plr_lf[f]}')

                flight_costs -= K[k]['OC'] * F_info[f]['distance']
                found = True

                F_SEQ1_fixed_info_dict[f] = {'Aircraft type':k,'Payload':weight,'Load Factor':F_plr_lf[f]}

        if not found:
            print(f'FLIGHT ARC {f} IS NOT BEING FLOWN BY ANY AIRCRAFT TYPE')
            logging.info(f'FLIGHT ARC {f} IS NOT BEING FLOWN BY ANY AIRCRAFT TYPE')

    # Convert dictionary to DataFrame
    df = pd.DataFrame.from_dict(F_SEQ1_fixed_info_dict, orient='index', columns=['Aircraft type','Payload','Load Factor'])
    # Reset index so the keys become a proper column
    df.reset_index(inplace=True)
    # Rename index column to 'Key'
    df.rename(columns={'index': 'Flight Arc'}, inplace=True)
    # Display the DataFrame
    print(df)

    R_transported = [r for r in R_dict.keys() for u in U_dict.keys() if z_dict.get((r,u)) is not None and z_dict.get((r, u)) >= 0.9]
    R_transported_ratio = len(R_transported)/len(R_dict)*100
    R_OD = {(o,d):[r for r,v in R_dict.items() if v[0]==o and v[1]==d] for o in airports_IATA for d in airports_IATA if d!=o}
    R_OD_transported = {od:[req for req in R_OD[od]
                            if req in R_transported]
                        for od in R_OD.keys()}
    R_OD_unfulfilled = {od:[req for req in R_OD[od]
                            if req not in R_transported]
                        for od in R_OD.keys()}
    R_OD_ratio = {od: np.round(len(R_OD_transported[od])/len(R_OD[od])*100,1) if
                len(R_OD[od]) > 0 else -1
                        for od in R_OD.keys()}

    R_unfulfilled = [r for r in R_dict if r not in R_transported]
    combined_weight =0
    for r in R_transported:
        combined_weight += R_dict[r][5]
    revenue = 0

    ##########################################################
    ### Note: average revenue hard-coded. A bit dangerous! ###
    ### To be fixed                                        ###
    ##########################################################
    for r in R_transported:
        revenue += R_dict[r][5] * R_dict[r][7] * 4000

    lost_revenue = 0
    for r in R_unfulfilled:
        lost_revenue += R_dict[r][5] * R_dict[r][7] * 4000
    average_rev_transported = revenue/len(R_transported)
    average_rev_unfulfilled = lost_revenue/len(R_unfulfilled)

    R_no_feature_transported  = [idx for idx in R_transported if R_dict[idx][8] == 0 and R_dict[idx][9] == 0]
    R_hazfeature_transported  = [idx for idx in R_transported if R_dict[idx][8] == 1 and R_dict[idx][9] == 0]
    R_tempfeature_transported = [idx for idx in R_transported if R_dict[idx][9] == 1 and R_dict[idx][8] == 0]
    R_bothfeature_transported = [idx for idx in R_transported if R_dict[idx][8] == 1 and R_dict[idx][9] == 1]

    total_chemical_count = sum(1 for key, value in R_dict.items() if value[4] == 'chemical')
    transported_chemical_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'chemical')
    percentage_chemical = transported_chemical_count / total_chemical_count
    print(f'Percentage of chemical requests transported: {percentage_chemical}')

    total_perishable_count = sum(1 for key, value in R_dict.items() if value[4] == 'perishable')
    transported_perishable_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'perishable')
    percentage_perishable = transported_perishable_count / total_perishable_count
    print(f'Percentage of perishable requests transported: {percentage_perishable}')

    total_heavy_count = sum(1 for key, value in R_dict.items() if value[4] == 'heavy')
    transported_heavy_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'heavy')
    percentage_heavy = transported_heavy_count / total_heavy_count
    print(f'Percentage of heavy requests transported: {percentage_heavy}')

    total_other_count = sum(1 for key, value in R_dict.items() if value[4] == 'other')
    transported_other_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'other')
    percentage_other = transported_other_count / total_other_count
    print(f'Percentage of other requests transported: {percentage_other}')

    ULDs_on_arc = {}
    ULDs_OD = {}
    ULD_used = []
    # Iterate through the original dictionary
    for (arc, u), value in y_dict.items():
        # If the arc is not already in the dictionary, add it with an empty list
        if arc not in ULDs_on_arc:
            ULDs_on_arc[arc] = []
        # Append the ULD to the list of ULDs for this arc
        ULDs_on_arc[arc].append(u)
        if (U_dict[u][0][0][0], U_dict[u][0][1][0]) not in ULDs_OD:
            ULDs_OD[(U_dict[u][0][0][0], U_dict[u][0][1][0])] = []
        if u not in ULDs_OD[(U_dict[u][0][0][0], U_dict[u][0][1][0])]:
            ULDs_OD[(U_dict[u][0][0][0], U_dict[u][0][1][0])].append(u)
        if u not in ULD_used:
            ULD_used.append(u)
    ratio_ULD_used = len(ULD_used)/len(U_dict) * 100
    U_uld_type_used   = {k:[idx for idx in ULD_used if U_dict[idx][2] ==k] for k in V_info}

    Requests_in_ULD = {}
    for (r, u), value in z_dict.items():
        # If the arc is not already in the dictionary, add it with an empty list
        if u not in Requests_in_ULD:
            Requests_in_ULD[u] = []
        # Append the ULD to the list of ULDs for this arc
        Requests_in_ULD[u].append(r)

    R_in_too_advanced_ULD = []
    for u in U_uld_type_used[1]:
        if u in Requests_in_ULD.keys():
            for r in R_no_feature_transported:
                if r in Requests_in_ULD[u]:
                    R_in_too_advanced_ULD.append(r)



    for u in U_uld_type_used[3]:
        if u in Requests_in_ULD.keys():
            for r in R_no_feature_transported:
                if r in Requests_in_ULD[u]:
                    R_in_too_advanced_ULD.append(r)

    R_nofeature_advancedULD_ratio = len(R_in_too_advanced_ULD)/len(R_no_feature_transported) * 100 if len(R_no_feature_transported) > 0 else -1

    average_uld_unit_cost = (len(U_uld_type_used[0]) * 0.105 + len(U_uld_type_used[1]) * 0.115 + len(U_uld_type_used[2]) * 0.1 + len(U_uld_type_used[3]) * 0.135 )/ len(ULD_used)

    print(f'Revenue with transported requests: {revenue}')
    logging.info(f'Revenue with transported requests: {revenue}')


    print(f'Path based revenue: {PATH_revenue}')
    logging.info(f'Path based revenue: {PATH_revenue}')

    print(f'Costs of the flights operated: {flight_costs}')
    print(f'Costs of routing the ULDs {uld_routing_costs}')

    logging.info(f'Costs of the flights operated: {flight_costs}')
    logging.info(f'Costs of routing the ULDs {uld_routing_costs}')

    SEQ1_fixed_solution = {}
    SEQ1_fixed_solution['Profit'] = revenue+flight_costs+uld_routing_costs
    SEQ1_fixed_solution['Revenue'] = revenue
    SEQ1_fixed_solution['Fleet_op_cost'] = flight_costs
    SEQ1_fixed_solution['R_f'] = R_on_f_full_info
    SEQ1_fixed_solution['F_SEQ1_info_dict'] = F_SEQ1_fixed_info_dict


    SEQ1_fixed_solution_file = os.path.join(instance_folder,'SEQ1_fixed_solution.pkl')
    ## Write the dictionaries to pickle files
    with open(SEQ1_fixed_solution_file, 'wb') as file:
        pickle.dump(SEQ1_fixed_solution, file)

    ########################################################################################
    ### RETRIEVE SOLUTION OF SEQUENTIAL MODEL WITH PARTIALLY FIXED ROUTING: SECOND STAGE ###
    ########################################################################################

    with open(x_file_name_SEQ_2_fixed, "rb") as file:
        x_dict = pickle.load(file)

    with open(y_file_name_SEQ_2_fixed, "rb") as file:
        y_dict = pickle.load(file)

    with open(z_file_name_SEQ_2_fixed, "rb") as file:
        z_dict = pickle.load(file)

    weight_counter = defaultdict(int)
    volume_counter = defaultdict(int)

    logging.info(V_info)

    uld_lf = []
    uld_vf = []

    F_SEQ2_fixed_info_dict = {} # Dictionary where we store which aircraft type is flying flight arc f

    for u in U_dict.keys():
        if U_dict[u][2] in (0, 1):
            uld_weight = 1.5
            uld_volume = 4.5
        elif U_dict[u][2] in (2, 3):
            uld_weight = 4.6
            uld_volume = 10.7
        for r in R_dict.keys():
            value = z_dict.get((r, u))
            if value:
                weight_counter[u] += R_dict[r][5]
                volume_counter[u] += R_dict[r][6]
        if weight_counter[u] > 0:
            uld_lf.append(weight_counter[u] / uld_weight)
            uld_vf.append(volume_counter[u] / uld_volume)
    F_plr_lf = {}
    flight_costs = 0
    ULDs_on_flight = {}
    R_on_f = {}
    R_on_f_full_info = {}
    for f in F_dict.keys():
        ULDs_on_flight[f] = []
        found = False  # To track if any k exists for the current f
        for k in K.keys():
            if x_dict.get((f, k)) is not None and x_dict.get((f, k)) >= 0.9:

                LD3_count = 0
                LD7_count = 0
                weight = 0

                for u in U_dict.keys():
                    if y_dict.get((f,u)) is not None and y_dict.get((f, u)) >= 0.9:
                        ULDs_on_flight[f].append(u)
                        if U_dict[u][2] in (0, 1):
                            LD3_count += 1
                        if U_dict[u][2] in (2, 3):
                            LD7_count += 1

                R_on_f[f] = [r for r in R_dict.keys() for u in ULDs_on_flight[f] if
                                z_dict.get((r, u)) is not None and z_dict.get((r, u)) >= 0.9]
                for r in R_on_f[f]:
                    weight += R_dict[r][5]

                F_plr_lf[f] = weight / W_fk[(f, k)]
                R_on_f_full_info[f] = {'requests':[r for r in R_dict.keys() for u in ULDs_on_flight[f] if
                                z_dict.get((r, u)) is not None and z_dict.get((r, u)) >= 0.9],
                                'weight':weight,
                                'max_weight':W_fk[(f, k)]}

                print(f'Flight arc {f} is being flown by aircraft type {k} and '
                    f'has {LD3_count} LD3 units and {LD7_count} LD7 units,'
                    f'and a payload range based load factor of {F_plr_lf[f]}')
                logging.info(f'Flight arc {f} is being flown by aircraft type {k} and '
                    f'has {LD3_count} LD3 units and {LD7_count} LD7 units,'
                    f'and a payload range based load factor of {F_plr_lf[f]}')

                flight_costs -= K[k]['OC'] * F_info[f]['distance']
                found = True

                F_SEQ2_fixed_info_dict[f] = {'Aircraft type':k,'Payload':weight,'Load Factor':F_plr_lf[f]}

        if not found:
            print(f'FLIGHT ARC {f} IS NOT BEING FLOWN BY ANY AIRCRAFT TYPE')
            logging.info(f'FLIGHT ARC {f} IS NOT BEING FLOWN BY ANY AIRCRAFT TYPE')

    # Convert dictionary to DataFrame
    df = pd.DataFrame.from_dict(F_SEQ2_fixed_info_dict, orient='index', columns=['Aircraft type','Payload','Load Factor'])
    # Reset index so the keys become a proper column
    df.reset_index(inplace=True)
    # Rename index column to 'Key'
    df.rename(columns={'index': 'Flight Arc'}, inplace=True)
    # Display the DataFrame
    print(df)

    R_transported = [r for r in R_dict.keys() for u in U_dict.keys() if z_dict.get((r,u)) is not None and z_dict.get((r, u)) >= 0.9]
    R_transported_ratio = len(R_transported)/len(R_dict)*100
    R_OD = {(o,d):[r for r,v in R_dict.items() if v[0]==o and v[1]==d] for o in airports_IATA for d in airports_IATA if d!=o}
    R_OD_transported = {od:[req for req in R_OD[od]
                            if req in R_transported]
                        for od in R_OD.keys()}
    R_OD_unfulfilled = {od:[req for req in R_OD[od]
                            if req not in R_transported]
                        for od in R_OD.keys()}
    R_OD_ratio = {od: np.round(len(R_OD_transported[od])/len(R_OD[od])*100,1) if
                len(R_OD[od]) > 0 else -1
                        for od in R_OD.keys()}

    R_unfulfilled = [r for r in R_dict if r not in R_transported]
    combined_weight =0
    for r in R_transported:
        combined_weight += R_dict[r][5]
    revenue = 0

    ##########################################################
    ### Note: average revenue hard-coded. A bit dangerous! ###
    ### To be fixed                                        ###
    ##########################################################
    for r in R_transported:
        revenue += R_dict[r][5] * R_dict[r][7] * 4000

    lost_revenue = 0
    for r in R_unfulfilled:
        lost_revenue += R_dict[r][5] * R_dict[r][7] * 4000
    average_rev_transported = revenue/len(R_transported)
    average_rev_unfulfilled = lost_revenue/len(R_unfulfilled)

    R_no_feature_transported  = [idx for idx in R_transported if R_dict[idx][8] == 0 and R_dict[idx][9] == 0]
    R_hazfeature_transported  = [idx for idx in R_transported if R_dict[idx][8] == 1 and R_dict[idx][9] == 0]
    R_tempfeature_transported = [idx for idx in R_transported if R_dict[idx][9] == 1 and R_dict[idx][8] == 0]
    R_bothfeature_transported = [idx for idx in R_transported if R_dict[idx][8] == 1 and R_dict[idx][9] == 1]

    total_chemical_count = sum(1 for key, value in R_dict.items() if value[4] == 'chemical')
    transported_chemical_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'chemical')
    percentage_chemical = transported_chemical_count / total_chemical_count
    print(f'Percentage of chemical requests transported: {percentage_chemical}')

    total_perishable_count = sum(1 for key, value in R_dict.items() if value[4] == 'perishable')
    transported_perishable_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'perishable')
    percentage_perishable = transported_perishable_count / total_perishable_count
    print(f'Percentage of perishable requests transported: {percentage_perishable}')

    total_heavy_count = sum(1 for key, value in R_dict.items() if value[4] == 'heavy')
    transported_heavy_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'heavy')
    percentage_heavy = transported_heavy_count / total_heavy_count
    print(f'Percentage of heavy requests transported: {percentage_heavy}')

    total_other_count = sum(1 for key, value in R_dict.items() if value[4] == 'other')
    transported_other_count = sum(1 for key in R_dict if key in R_transported and R_dict[key][4] == 'other')
    percentage_other = transported_other_count / total_other_count
    print(f'Percentage of other requests transported: {percentage_other}')

    ULDs_on_arc = {}
    ULDs_OD = {}
    ULD_used = []
    # Iterate through the original dictionary
    for (arc, u), value in y_dict.items():
        # If the arc is not already in the dictionary, add it with an empty list
        if arc not in ULDs_on_arc:
            ULDs_on_arc[arc] = []
        # Append the ULD to the list of ULDs for this arc
        ULDs_on_arc[arc].append(u)
        if (U_dict[u][0][0][0], U_dict[u][0][1][0]) not in ULDs_OD:
            ULDs_OD[(U_dict[u][0][0][0], U_dict[u][0][1][0])] = []
        if u not in ULDs_OD[(U_dict[u][0][0][0], U_dict[u][0][1][0])]:
            ULDs_OD[(U_dict[u][0][0][0], U_dict[u][0][1][0])].append(u)
        if u not in ULD_used:
            ULD_used.append(u)
    ratio_ULD_used = len(ULD_used)/len(U_dict) * 100
    U_uld_type_used   = {k:[idx for idx in ULD_used if U_dict[idx][2] ==k] for k in V_info}

    Requests_in_ULD = {}
    for (r, u), value in z_dict.items():
        # If the arc is not already in the dictionary, add it with an empty list
        if u not in Requests_in_ULD:
            Requests_in_ULD[u] = []
        # Append the ULD to the list of ULDs for this arc
        Requests_in_ULD[u].append(r)

    R_in_too_advanced_ULD = []
    for u in U_uld_type_used[1]:
        if u in Requests_in_ULD.keys():
            for r in R_no_feature_transported:
                if r in Requests_in_ULD[u]:
                    R_in_too_advanced_ULD.append(r)



    for u in U_uld_type_used[3]:
        if u in Requests_in_ULD.keys():
            for r in R_no_feature_transported:
                if r in Requests_in_ULD[u]:
                    R_in_too_advanced_ULD.append(r)

    R_nofeature_advancedULD_ratio = len(R_in_too_advanced_ULD)/len(R_no_feature_transported) * 100 if len(R_no_feature_transported) > 0 else -1

    average_uld_unit_cost = (len(U_uld_type_used[0]) * 0.105 + len(U_uld_type_used[1]) * 0.115 + len(U_uld_type_used[2]) * 0.1 + len(U_uld_type_used[3]) * 0.135 )/ len(ULD_used)

    uld_routing_costs = 0
    for f in F_dict.keys():
        ULDs_to_try = ULDs_on_arc.get(f)
        if ULDs_to_try == None:
            continue
        for u in ULDs_to_try:
            uld_type = U_dict[u][2]
            uld_routing_costs -= V_info[uld_type][5] * F_info[f]['distance']

    print(f'Revenue with transported requests: {revenue}')
    logging.info(f'Revenue with transported requests: {revenue}')


    print(f'Path based revenue: {PATH_revenue}')
    logging.info(f'Path based revenue: {PATH_revenue}')

    print(f'Costs of the flights operated: {flight_costs}')
    print(f'Costs of routing the ULDs {uld_routing_costs}')

    logging.info(f'Costs of the flights operated: {flight_costs}')
    logging.info(f'Costs of routing the ULDs {uld_routing_costs}')

    SEQ2_fixed_solution = {}
    SEQ2_fixed_solution['Profit'] = revenue+flight_costs+uld_routing_costs
    SEQ2_fixed_solution['Revenue'] = revenue
    SEQ2_fixed_solution['Fleet_op_cost'] = flight_costs
    SEQ2_fixed_solution['ULD_op_cost'] = uld_routing_costs
    SEQ2_fixed_solution['R_f'] = R_on_f_full_info
    SEQ2_fixed_solution['F_SEQ2_info_dict'] = F_SEQ2_fixed_info_dict


    SEQ2_fixed_solution_file = os.path.join(instance_folder,'SEQ2_fixed_solution.pkl')
    ## Write the dictionaries to pickle files
    with open(SEQ2_fixed_solution_file, 'wb') as file:
        pickle.dump(SEQ2_fixed_solution, file)

else:
    pass


