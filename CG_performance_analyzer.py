#%%
import numpy as np
import pandas as pd
import os
import pickle
import re

cwd = os.getcwd()

folder_name_list = ['full_H_35_restricted_subset15_5it_w_max_cap200_seed42_CG',
                    'full_H_50_restricted_subset15_5it_w_max_cap200_seed42_CG',
                    'full_H_65_restricted_subset15_5it_w_max_cap200_seed42_CG',
                    'full_H_80_restricted_subset15_5it_w_max_cap200_seed42_CG',
                    'full_M_35_restricted_subset15_5it_w_max_cap200_seed42_CG',
                    'full_M_50_restricted_subset15_5it_w_max_cap200_seed42_CG',
                    'full_M_65_restricted_subset15_5it_w_max_cap200_seed42_CG',
                    'full_M_80_restricted_subset15_5it_w_max_cap200_seed42_CG',
                    'full_L_35_restricted_subset15_5it_w_max_cap200_seed42_CG',
                    'full_L_50_restricted_subset15_5it_w_max_cap200_seed42_CG',
                    'full_L_65_restricted_subset15_5it_w_max_cap200_seed42_CG',
                    'full_L_80_restricted_subset15_5it_w_max_cap200_seed42_CG']

# folder_name_list = ['full_H_35_restricted_subset15_25it_w_max_cap200_seed42_CG',
#                     'full_H_50_restricted_subset15_25it_w_max_cap200_seed42_CG',
#                     'full_H_65_restricted_subset15_25it_w_max_cap200_seed42_CG',
#                     'full_H_80_restricted_subset15_25it_w_max_cap200_seed42_CG',
#                     'full_M_35_restricted_subset15_25it_w_max_cap200_seed42_CG',
#                     'full_M_50_restricted_subset15_25it_w_max_cap200_seed42_CG',
#                     'full_M_65_restricted_subset15_25it_w_max_cap200_seed42_CG',
#                     'full_M_80_restricted_subset15_25it_w_max_cap200_seed42_CG',
#                     'full_L_35_restricted_subset15_25it_w_max_cap200_seed42_CG',
#                     'full_L_50_restricted_subset15_25it_w_max_cap200_seed42_CG',
#                     'full_L_65_restricted_subset15_25it_w_max_cap200_seed42_CG',
#                     'full_L_80_restricted_subset15_25it_w_max_cap200_seed42_CG']


# Initialize list storing summary data per instance
rows = []

for folder_name in folder_name_list:
    N_it_max  = int(re.search(r'_(\d+)it', folder_name).group(1))
    max_paths = int(re.search(r'cap(\d+)_', folder_name).group(1))

    full_path = os.path.join(cwd, 'pickle_files', folder_name)

    # # Retrieve pickle file
    # with open(os.path.join(full_path, 'P_dict.pkl'), 'rb') as f:
    #     U_dict = pickle.load(f)
    #     R_dict = pickle.load(f)
    #     F_dict = pickle.load(f)
    #     A_all_dict_2 = pickle.load(f)
    #     P_dict = pickle.load(f)
    #     C_up = pickle.load(f)
    #     R_up = pickle.load(f)
    #     W_up = pickle.load(f)
    #     paths_per_it_dict = pickle.load(f)
    #     elapsed_time_global = pickle.load(f)
    #     RMP_sol_dict =pickle.load(f)

    with open(os.path.join(full_path, 'P_dict.pkl'), 'rb') as f:
        all_data = pickle.load(f)

    U_dict = all_data["U_dict"]
    R_dict = all_data["R_dict"]
    F_dict = all_data["F_dict"]
    A_all_dict_2 = all_data["A_all_dict_2"]
    P_dict = all_data["P_dict"]
    C_up = all_data["C_up"]
    R_up = all_data["R_up"]
    W_up = all_data["W_up"]
    paths_per_it_dict = all_data["paths_per_it_dict"]
    elapsed_time_global = all_data["elapsed_time_global"]
    RMP_sol_dict = all_data["RMP_sol_dict"]

    P_u = {u: [p for p, p_values in P_dict.items() if u + len(A_all_dict_2) in p_values['arc_path']] for u in U_dict}
    P_r = {r: [p for p, p_values in P_dict.items() if r in p_values['packing']] for r in R_dict.keys()}
    #P_f = {f: [p for p, p_values in P_dict.items() if f in p_values['arc_path']] for f in F_dict.keys()}

    #%%
    print(f'Number of ULDs: {len(U_dict.keys())}')
    print(f'Number of original paths: {len(P_dict)-sum(paths_per_it_dict.values())}')
    print(f'Number of additional paths: {sum(paths_per_it_dict.values())}')
    print(f'Number of overall paths: {len(P_dict)}')

    lengths_U = [len(v) for v in P_u.values()]
    lengths_R = [len(v) for v in P_r.values()]

    stats = {
        **{str(i+1): paths_per_it_dict.get(i, 0) for i in range(0,N_it_max)},
        "min_U": min(lengths_U),
        "max_U": max(lengths_U),
        "mean_U": np.round(sum(lengths_U) / len(lengths_U), 1),
        "min_R": min(lengths_R),
        "max_R": max(lengths_R),
        "mean_R": np.round(sum(lengths_R) / len(lengths_R), 1),
        "R_geq_max_paths": sum(l >= max_paths for l in lengths_R)
    }

    comp_level = folder_name.split('_')[1]
    payload = int(folder_name.split('_')[2])

    stats["comp_level"]    = comp_level
    stats["Payload"]       = payload
    stats["ULDs"]          = len(U_dict.keys())
    stats["overall_paths"] = sum(paths_per_it_dict.values())
    stats["R"]             = len(R_dict.keys())

    rows.append(stats)

    print(stats)
    print(RMP_sol_dict)

df   = pd.DataFrame(rows)
cols = ['comp_level', 'Payload', 'ULDs', 'overall_paths','R'] + [c for c in df.columns if c not in  
       ['comp_level', 'Payload', 'ULDs', 'overall_paths','R']]
df   = df[cols]

# %%

latex_table = df.to_latex(
    index=False,
    float_format="%.1f",
    caption="Summary statistics of paths per ULD and request.",
    label="tab:paths_stats"
)

print(latex_table)







