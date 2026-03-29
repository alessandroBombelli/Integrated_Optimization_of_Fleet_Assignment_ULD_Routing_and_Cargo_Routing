import subprocess
import sys
import os
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Define colors
INFORMS_orange     = "#e88900"
INFORMS_darkorange = "#e64300"
INFORMS_dark       = "#6b0a1f"

# Define the orange palette
orange_palette = [
    (1.0, 0.85, 0.7),  # Light Peach
    (1.0, 0.7, 0.4),   # Soft Apricot
    (1.0, 0.55, 0.1),  # Golden Orange
    (0.91, 0.4, 0.1),  # Deep Orange
    (0.8, 0.3, 0.0),   # Burnt Orange
    (0.6, 0.2, 0.0)    # Dark Rust
]

plt.close("all")

cwd                = os.getcwd()
# file_CG            = os.path.join(cwd,"comparison","full_M_65_subset15_restricted_seed42","CG_solution.pkl")
# file_SEQ1          = os.path.join(cwd,"comparison","full_M_65_subset15_restricted_seed42","SEQ1_solution.pkl")
# file_SEQ2          = os.path.join(cwd,"comparison","full_M_65_subset15_restricted_seed42","SEQ2_solution.pkl")
# file_K             = os.path.join(cwd,"comparison","full_M_65_subset15_restricted_seed42","K.pkl")
# file_F_info        = os.path.join(cwd,"comparison","full_M_65_subset15_restricted_seed42","F_info.pkl")
# file_F_dict        = os.path.join(cwd,"comparison","full_M_65_subset15_restricted_seed42","F_dict.pkl")
# file_N_dict_idx_at = os.path.join(cwd,"comparison","full_M_65_subset15_restricted_seed42","N_dict_idx_at.pkl")
# file_N_dict_at_idx = os.path.join(cwd,"comparison","full_M_65_subset15_restricted_seed42","N_dict_at_idx.pkl")

# file_CG            = os.path.join(cwd,"comparison","full_L_50_subset15_restricted_seed42","CG_solution.pkl")
# file_SEQ1          = os.path.join(cwd,"comparison","full_L_50_subset15_restricted_seed42","SEQ1_solution.pkl")
# file_SEQ2          = os.path.join(cwd,"comparison","full_L_50_subset15_restricted_seed42","SEQ2_solution.pkl")
# file_K             = os.path.join(cwd,"comparison","full_L_50_subset15_restricted_seed42","K.pkl")
# file_F_info        = os.path.join(cwd,"comparison","full_L_50_subset15_restricted_seed42","F_info.pkl")
# file_F_dict        = os.path.join(cwd,"comparison","full_L_50_subset15_restricted_seed42","F_dict.pkl")
# file_N_dict_idx_at = os.path.join(cwd,"comparison","full_L_50_subset15_restricted_seed42","N_dict_idx_at.pkl")
# file_N_dict_at_idx = os.path.join(cwd,"comparison","full_L_50_subset15_restricted_seed42","N_dict_at_idx.pkl")

file_CG            = os.path.join(cwd,"comparison","full_L_65_subset15_restricted_seed42","CG_solution.pkl")
file_SEQ1          = os.path.join(cwd,"comparison","full_L_65_subset15_restricted_seed42","SEQ1_solution.pkl")
file_SEQ2          = os.path.join(cwd,"comparison","full_L_65_subset15_restricted_seed42","SEQ2_solution.pkl")
file_K             = os.path.join(cwd,"comparison","full_L_65_subset15_restricted_seed42","K.pkl")
file_F_info        = os.path.join(cwd,"comparison","full_L_65_subset15_restricted_seed42","F_info.pkl")
file_F_dict        = os.path.join(cwd,"comparison","full_L_65_subset15_restricted_seed42","F_dict.pkl")
file_N_dict_idx_at = os.path.join(cwd,"comparison","full_L_65_subset15_restricted_seed42","N_dict_idx_at.pkl")
file_N_dict_at_idx = os.path.join(cwd,"comparison","full_L_65_subset15_restricted_seed42","N_dict_at_idx.pkl")

# Check if a sequential solution with partially fixed routing exists
fixed_routing_folder = os.path.join(cwd,"pickle_files","full_L_65_subset15_restricted_seed42_SEQ","results_with_partially_fixed_routing")
seq_with_fixed_routing = False
if os.path.isdir(fixed_routing_folder):
    seq_with_fixed_routing = True
    file_SEQ1_fixed        = os.path.join(cwd,"comparison","full_L_65_subset15_restricted_seed42","SEQ1_fixed_solution.pkl")
    file_SEQ2_fixed        = os.path.join(cwd,"comparison","full_L_65_subset15_restricted_seed42","SEQ2_fixed_solution.pkl")


with open(file_CG, "rb") as file:
    CG_solution = pickle.load(file)
with open(file_SEQ1, "rb") as file:
    SEQ1_solution = pickle.load(file)
with open(file_SEQ2, "rb") as file:
    SEQ2_solution = pickle.load(file)
with open(file_K, "rb") as file:
    K = pickle.load(file)
with open(file_F_info, "rb") as file:
    F_info = pickle.load(file)
with open(file_F_dict, "rb") as file:
    F_dict = pickle.load(file)
with open(file_N_dict_idx_at, "rb") as file:
    N_dict_idx_at = pickle.load(file)
with open(file_N_dict_at_idx, "rb") as file:
    N_dict_at_idx = pickle.load(file)

F_CG_info_dict   = CG_solution["F_CG_info_dict"]
F_SEQ1_info_dict = SEQ1_solution["F_SEQ1_info_dict"]
F_SEQ2_info_dict = SEQ2_solution["F_SEQ2_info_dict"]

# Convert dictionary to DataFrame
df_CG = pd.DataFrame.from_dict(F_CG_info_dict, orient='index', columns=['Aircraft type','Payload','Load Factor'])
# Reset index so the keys become a proper column
df_CG.reset_index(inplace=True)
# Rename index column to 'Key'
df_CG.rename(columns={'index': 'Flight Arc'}, inplace=True)
# Display the DataFrame
#print(df_CG)

# Convert dictionary to DataFrame
df_SEQ1 = pd.DataFrame.from_dict(F_SEQ1_info_dict, orient='index', columns=['Aircraft type','Payload','Load Factor'])
# Reset index so the keys become a proper column
df_SEQ1.reset_index(inplace=True)
# Rename index column to 'Key'
df_SEQ1.rename(columns={'index': 'Flight Arc'}, inplace=True)
# Display the DataFrame
#print(df_SEQ1)

# Convert dictionary to DataFrame
df_SEQ2 = pd.DataFrame.from_dict(F_SEQ2_info_dict, orient='index', columns=['Aircraft type','Payload','Load Factor'])
# Reset index so the keys become a proper column
df_SEQ2.reset_index(inplace=True)
# Rename index column to 'Key'
df_SEQ2.rename(columns={'index': 'Flight Arc'}, inplace=True)
# Display the DataFrame
#print(df_SEQ2)

# Merge on "flight arc" while keeping it only once
merged_df = pd.merge(df_CG, df_SEQ1,     on='Flight Arc')
merged_df = pd.merge(merged_df, df_SEQ2, on='Flight Arc')

print(CG_solution["Revenue"])
print(CG_solution["Fleet_op_cost"])
print(SEQ1_solution["Revenue"])
print(SEQ1_solution["Fleet_op_cost"])
print(SEQ2_solution["Revenue"])
print(SEQ2_solution["Fleet_op_cost"])

mask_00 = (merged_df["Aircraft type_x"]==0) & (merged_df["Aircraft type"]==0)
mask_11 = (merged_df["Aircraft type_x"]==1) & (merged_df["Aircraft type"]==1)
mask_01 = (merged_df["Aircraft type_x"]==0) & (merged_df["Aircraft type"]==1)
mask_10 = (merged_df["Aircraft type_x"]==1) & (merged_df["Aircraft type"]==0)

df_00 = merged_df[mask_00].reset_index()
df_11 = merged_df[mask_11].reset_index()
df_01 = merged_df[mask_01].reset_index()
df_10 = merged_df[mask_10].reset_index()

airports   = sorted(list(set([v[0] for v in N_dict_idx_at.values() if v[0] != "Source" and v[0] != "Sink"])))
timestamps = sorted(list(set([v[1] for v in N_dict_idx_at.values() if v[0] != "Source" and v[0] != "Sink"])))


###########################################################
### Applying a mapping so that airports become a number ###
### and timestamps are linearly scaled as well between  ###
### 0 and an user-defined upper bound                   ###
###########################################################

airport_to_idx_dict   = {airp:i for i,airp in enumerate(airports)}
max_value             = 20
timestamp_to_idx_dict = {timestamp:np.round(max_value*(timestamp-min(timestamps))/(max(timestamps)-min(timestamps)),1)
                          for timestamp in timestamps}


##########################################
### PLOTTING THE 2 NETWORKS SEPARATELY ###
##########################################
mask_INT_0 = (merged_df["Aircraft type_x"]==0)
mask_INT_1 = (merged_df["Aircraft type_x"]==1)
mask_SEQ_0 = (merged_df["Aircraft type"]==0)
mask_SEQ_1 = (merged_df["Aircraft type"]==1)

df_INT_0 = merged_df[mask_INT_0].reset_index()
df_INT_1 = merged_df[mask_INT_1].reset_index()
df_SEQ_0 = merged_df[mask_SEQ_0].reset_index()
df_SEQ_1 = merged_df[mask_SEQ_1].reset_index()

# Convert to UTC
utc_times = [datetime.fromtimestamp(ts, tz=timezone.utc) for ts in timestamps]

width_line  = 2.0
width_line2 = 3.0

# Integrated model
fig,ax = plt.subplots()
for idx,row in enumerate(df_INT_0.iterrows()):
    if idx == 0:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=INFORMS_orange,label="B747-400BCF")
    else:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=INFORMS_orange)

for idx,row in enumerate(df_INT_1.iterrows()):
    if idx == 0:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=INFORMS_dark,label="B747-400ERF")
    else:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=INFORMS_dark)

# Format the x-axis to show time every 12 hours
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))  # Show time every 12 hours
# Rotate date labels for better readability
plt.xticks(rotation=30,fontsize=6)
ax.set_yticks([idx for idx,_ in enumerate(airports)])
ax.set_yticklabels(airports)
plt.xlabel("Time [Y-M-D HH:MM]",fontsize=12)
plt.ylabel("Airport",fontsize=12)
plt.legend(loc="best")
ax.grid("True")
plt.savefig("L_65_INT.png", dpi=600, bbox_inches="tight")

# Sequential model
fig,ax = plt.subplots()
for idx,row in enumerate(df_SEQ_0.iterrows()):
    if idx == 0:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=INFORMS_orange,label="B747-400BCF")
    else:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=INFORMS_orange)

for idx,row in enumerate(df_SEQ_1.iterrows()):
    if idx == 0:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=INFORMS_dark,label="B747-400ERF")
    else:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=INFORMS_dark)

# Format the x-axis to show time every 12 hours
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))  # Show time every 12 hours
# Rotate date labels for better readability
plt.xticks(rotation=30,fontsize=6)
ax.set_yticks([idx for idx,_ in enumerate(airports)])
ax.set_yticklabels(airports)
plt.xlabel("Time [Y-M-D HH:MM]",fontsize=12)
plt.ylabel("Airport",fontsize=12)
plt.legend(loc="best")
ax.grid("True")
plt.savefig("L_65_SEQ.png", dpi=600, bbox_inches="tight")

############################################
### Plotting now the two models combined ###
############################################
import seaborn as sns

palette = sns.color_palette(["#D73027", "#FC8D59", "#FEE08B", "#FDAE61", "#E31A1C"])

# palette = ['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B3', 
#            '#937860', '#DA8BC3', '#8C8C8C', '#CCB974', '#64B5CD']

# palette = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#F0E442', 
#            '#56B4E9', '#E69F00']

palette = ['#117733', '#332288', '#44AA99', '#88CCEE', '#DDCC77', 
           '#CC6677', '#AA4499', '#882255']



# Both models choose B747-400BCF
fig,ax = plt.subplots()
for idx,row in enumerate(df_00.iterrows()):
    if idx == 0:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],color=palette[0],linewidth=width_line,label="B747-400BCF both")
    else:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=palette[0])

# Both models choose B747-400ERF
for idx,row in enumerate(df_11.iterrows()):
    if idx == 0:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=palette[1],label="B747-400ERF both")
    else:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=palette[1])

# Integrated chooses B747-400BCF, sequential chooses B747-400ERF
for idx,row in enumerate(df_01.iterrows()):
    if idx == 0:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=palette[5],label="B747-400BCF int., B747-400ERF seq.")
    else:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=palette[5])



# Integrated chooses B747-400ERF, sequential chooses B747-400BCF
for idx,row in enumerate(df_10.iterrows()):
    if idx == 0:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=palette[3],label="B747-400ERF int., B747-400BCF seq.")
    else:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=palette[3])

# Format the x-axis to show time every 12 hours
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))  # Show time every 12 hours
# Rotate date labels for better readability
plt.xticks(rotation=30,fontsize=6)
ax.set_yticks([idx for idx,_ in enumerate(airports)])
ax.set_yticklabels(airports)
plt.xlabel("Time [Y-M-D HH:MM]",fontsize=12)
plt.ylabel("Airport",fontsize=12)
plt.legend(loc="best")
ax.grid("True")
plt.savefig("L_65_INT_vs_SEQ.png", dpi=600, bbox_inches="tight")

##############################################
### Same plot as above, but easier to read ###
##############################################
fig,ax = plt.subplots(figsize=(8, 6))
# Both models choose B747-400BCF
for idx,row in enumerate(df_00.iterrows()):
    if idx == 0:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],color=INFORMS_orange,linewidth=width_line,alpha=0.5)
    else:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,alpha=0.5,color=INFORMS_orange)

# Both models choose B747-400ERF
for idx,row in enumerate(df_11.iterrows()):
    if idx == 0:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=INFORMS_dark,alpha=0.5)
    else:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=INFORMS_dark,alpha=0.5)

# Integrated chooses B747-400BCF, sequential chooses B747-400ERF
for idx,row in enumerate(df_01.iterrows()):
    if idx == 0:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line2,color=INFORMS_orange,label="B747-400BCF")
    else:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line2,color=INFORMS_orange)



# Integrated chooses B747-400ERF, sequential chooses B747-400BCF
for idx,row in enumerate(df_10.iterrows()):
    if idx == 0:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line2,color=INFORMS_dark,label="B747-400ERF")
    else:
        this_f = int(row[1]["Flight Arc"])
        origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
        destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
        origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
        destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line2,color=INFORMS_dark)

# Format the x-axis to show time every 12 hours
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))  # Show time every 12 hours
# Rotate date labels for better readability
plt.xticks(rotation=30,fontsize=6)
ax.set_yticks([idx for idx,_ in enumerate(airports)])
ax.set_yticklabels(airports)
plt.xlabel("Time [Y-M-D HH:MM]",fontsize=12)
plt.ylabel("Airport",fontsize=12)
plt.legend(loc="best")
ax.grid("True")
plt.savefig("L_65_INT_vs_SEQ_v2.png", dpi=600, bbox_inches="tight")










print("")
for idx_flight in df_01["Flight Arc"]:
    print(idx_flight)
    print(F_dict[idx_flight])
    print(N_dict_idx_at[F_dict[idx_flight][0]])
    print(N_dict_idx_at[F_dict[idx_flight][1]])
    print(datetime.fromtimestamp(N_dict_idx_at[F_dict[idx_flight][0]][1], tz=timezone.utc))
    print("")

print(df_01)

if seq_with_fixed_routing is True:
    print("Analyzing sequential model with partially fixed routing")
    with open(file_SEQ1_fixed, "rb") as file:
        SEQ1_fixed_solution = pickle.load(file)
    with open(file_SEQ2_fixed, "rb") as file:
        SEQ2_fixed_solution = pickle.load(file)
    F_SEQ1_fixed_info_dict = SEQ1_fixed_solution["F_SEQ1_info_dict"]
    F_SEQ2_fixed_info_dict = SEQ2_fixed_solution["F_SEQ2_info_dict"]

    # Convert dictionary to DataFrame
    df_SEQ2_fixed = pd.DataFrame.from_dict(F_SEQ2_fixed_info_dict, orient='index', columns=['Aircraft type','Payload','Load Factor'])
    # Reset index so the keys become a proper column
    df_SEQ2_fixed.reset_index(inplace=True)
    # Rename index column to 'Key'
    df_SEQ2_fixed.rename(columns={'index': 'Flight Arc'}, inplace=True)
    # Display the DataFrame
    print(df_SEQ2_fixed)

    mask_SEQ_fixed_0 = (df_SEQ2_fixed["Aircraft type"]==0)
    mask_SEQ_fixed_1 = (df_SEQ2_fixed["Aircraft type"]==1)

    df_SEQ_fixed_0 = df_SEQ2_fixed[mask_SEQ_fixed_0].reset_index()
    df_SEQ_fixed_1 = df_SEQ2_fixed[mask_SEQ_fixed_1].reset_index()

    fig,ax = plt.subplots()
    for idx,row in enumerate(df_SEQ_fixed_0.iterrows()):
        if idx == 0:
            this_f = int(row[1]["Flight Arc"])
            origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
            destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
            origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
            destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
            plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=INFORMS_orange,label="B747-400BCF")
        else:
            this_f = int(row[1]["Flight Arc"])
            origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
            destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
            origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
            destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
            plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=INFORMS_orange)

    for idx,row in enumerate(df_SEQ_fixed_1.iterrows()):
        if idx == 0:
            this_f = int(row[1]["Flight Arc"])
            origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
            destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
            origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
            destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
            plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=INFORMS_dark,label="B747-400ERF")
        else:
            this_f = int(row[1]["Flight Arc"])
            origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
            destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
            origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
            destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
            plt.plot([origin_time,destination_time],[origin_airport,destination_airport],linewidth=width_line,color=INFORMS_dark)

    # Format the x-axis to show time every 12 hours
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))  # Show time every 12 hours
    # Rotate date labels for better readability
    plt.xticks(rotation=30,fontsize=6)
    ax.set_yticks([idx for idx,_ in enumerate(airports)])
    ax.set_yticklabels(airports)
    plt.xlabel("Time [Y-M-D HH:MM]",fontsize=12)
    plt.ylabel("Airport",fontsize=12)
    plt.legend(loc="best")
    ax.grid("True")
    plt.savefig("L_65_SEQ_fixed_routing.png", dpi=600, bbox_inches="tight")

plt.show(block=False)

##################################################################################
### Plotting full schedule and partial schedule to produce plots for the paper ###
##################################################################################

fig,ax = plt.subplots(figsize=(12, 9))
for idx,row in enumerate(merged_df.iterrows()):
    this_f = int(row[1]["Flight Arc"])
    origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
    destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
    origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
    destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
    plt.plot([origin_time,destination_time],[origin_airport,destination_airport],color=INFORMS_orange,linewidth=width_line2,alpha=1)

# Format the x-axis to show time every 12 hours
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))  # Show time every 12 hours
# Rotate date labels for better readability
plt.xticks(rotation=30,fontsize=6)
ax.set_yticks([idx for idx,_ in enumerate(airports)])
ax.set_yticklabels(airports)
plt.xlabel("Time [Y-M-D HH:MM]",fontsize=12)
plt.ylabel("Airport",fontsize=12)
plt.legend(loc="best")
ax.grid("True")
plt.savefig("full_schedule.png", dpi=600, bbox_inches="tight")
plt.show(block=False)

dt       = datetime(2024, 6, 27, 6, 00)
dt_aware = dt.replace(tzinfo=timezone.utc)
fig,ax = plt.subplots(figsize=(12, 9))
for idx,row in enumerate(merged_df.iterrows()):
    this_f = int(row[1]["Flight Arc"])
    origin_airport      = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][0]][0]]
    destination_airport = airport_to_idx_dict[N_dict_idx_at[F_dict[this_f][1]][0]]
    origin_time         = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][0]][1], tz=timezone.utc)
    destination_time    = datetime.fromtimestamp(N_dict_idx_at[F_dict[this_f][1]][1], tz=timezone.utc)
    if destination_time <= dt_aware:
        plt.plot([origin_time,destination_time],[origin_airport,destination_airport],color=INFORMS_orange,linewidth=width_line2,alpha=1)

# Format the x-axis to show time every 12 hours
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))  # Show time every 12 hours
# Rotate date labels for better readability
plt.xticks(rotation=30,fontsize=6)
ax.set_yticks([idx for idx,_ in enumerate(airports)])
ax.set_yticklabels(airports)
plt.xlabel("Time [Y-M-D HH:MM]",fontsize=12)
plt.ylabel("Airport",fontsize=12)
plt.legend(loc="best")
ax.grid("True")
plt.savefig("reduced_schedule.png", dpi=600, bbox_inches="tight")
plt.show(block=False)

######################################################
### Plotting final results in terms of profit etc. ###
######################################################
print("INTEGRATED MODEL:")
print("Profit of integrated model:",CG_solution["Profit"])
print("Revenue of integrated model:",CG_solution["Revenue"])
print("Fleet op. cost of integrated model:",CG_solution["Fleet_op_cost"])
print("")
print("SEQUENTIAL MODEL:")
print("Profit of sequential model first stage:",SEQ1_solution["Profit"])
print("Revenue of sequential model first stage:",SEQ1_solution["Revenue"])
print("Fleet op. cost of sequential model first stage:",SEQ1_solution["Fleet_op_cost"])
print("Profit of sequential model second stage:",SEQ2_solution["Profit"])
print("Revenue of sequential model second stage:",SEQ2_solution["Revenue"])
print("Fleet op. cost of sequential model second stage:",SEQ2_solution["Fleet_op_cost"])
print("")

if seq_with_fixed_routing is True:
    print("SEQUENTIAL MODEL WITH PARTIALLY FIXED ROUTING:")
    print("Profit of sequential model first stage:",SEQ1_fixed_solution["Profit"])
    print("Revenue of sequential model first stage:",SEQ1_fixed_solution["Revenue"])
    print("Fleet op. cost of sequential model first stage:",SEQ1_fixed_solution["Fleet_op_cost"])
    print("Profit of sequential model second stage:",SEQ2_fixed_solution["Profit"])
    print("Revenue of sequential model second stage:",SEQ2_fixed_solution["Revenue"])
    print("Fleet op. cost of sequential model second stage:",SEQ2_fixed_solution["Fleet_op_cost"])




input("Press Enter to exit...") 



