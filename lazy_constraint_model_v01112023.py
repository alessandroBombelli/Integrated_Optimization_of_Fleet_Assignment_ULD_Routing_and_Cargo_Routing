# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 10:42:25 2023

@author: abombelli
"""

import numpy as np
import pandas as pd
import os
import igraph as ig
from geopy.distance import great_circle
import random
from gurobipy import Model,GRB,LinExpr,quicksum

random.seed(42)
# random.seed(50) is interesting as there are some airports that cannot
# be reached directly
cwd         = os.getcwd()

# ID of instance
ID_instance = 1

# Importing airports
df_airports         = pd.read_excel(os.path.join(cwd,'airports_info.xlsx'))
airports_IATA       = list(df_airports['IATA'])
airports_region     = list(df_airports['region'])
airports_lat        = list(df_airports['lat'])
airports_lon        = list(df_airports['lon'])

# Fleet types and number
K = {0:[1,'B767-I'],
     1:[1,'B767-II']}

# Data on payload-range diagram. For now, we just use the B767 in the
# two variants (that are the same in terms of payload range). The three lists
# per aircraft type contain 2 elements, that represent the (Y,X) points in the
# (range,payload) diagram depicting the point where we cannot travel any
# longer with maximum payload, the point where we are capacitated by fuel, 
# and the maximum range at zero payload

PRD = {0:[[5,6000],[2,11000],[0,13500]],
       1:[[5,6000],[2,11000],[0,13500]]}
       #1:[[55,6000],[30,11000],[0,13500]]}

def compute_max_payload(PRD,k,distance):
    PRD_k = PRD[k]
    # Here we can fly with max. payload
    if distance <= PRD_k[0][1]:
        payload = PRD_k[0][0]
    # Here the MTOW is limiting
    elif distance <= PRD_k[1][1]:
        payload = PRD_k[0][0]*(distance-PRD_k[1][1])/(PRD_k[0][1]-PRD_k[1][1])+\
                  PRD_k[1][0]*(PRD_k[0][1]-distance)/(PRD_k[0][1]-PRD_k[1][1])
    # Here we are at full fuel capacity
    elif distance <= PRD_k[2][1]:
        payload = PRD_k[1][0]*(distance-PRD_k[2][1])/(PRD_k[1][1]-PRD_k[2][1])+\
                  PRD_k[2][0]*(PRD_k[1][1]-distance)/(PRD_k[1][1]-PRD_k[2][1])
    # If we enter this else, the distance is too much even if we were flying
    # with no payload. Hence, the direct flight is not possible in the
    # first place
    else:
        payload = -1
        
        
    return payload
    
    

# Determining maximum range across all fleet types
max_range_fleet = max([v[2][1] for k,v in PRD.items()])

# Compute airport distance matrix (only upper triangular part), and then sum
# the transpose
airport_distance_matrix     = np.zeros([len(df_airports),len(df_airports)])
for i,row_i in df_airports.iterrows():
    for j,row_j in df_airports.iterrows():
        if j>i:
            airport_distance_matrix[i][j] = great_circle((row_i.lat,row_i.lon),(row_j.lat,row_j.lon)).kilometers

airport_distance_matrix = airport_distance_matrix + np.transpose(airport_distance_matrix)

# Binary matrix. Unitary values if the (i,j) airport pair can be reached 
# considering the maximum range that was computed above
airport_reachability_matrix = np.zeros([len(df_airports),len(df_airports)])

for i in range(0,len(airport_distance_matrix)):
    for j in range(0,len(airport_distance_matrix)):
        if j>i:
            airport_reachability_matrix[i][j] = 1 if airport_distance_matrix[i][j] <= max_range_fleet else 0 

airport_reachability_matrix = airport_reachability_matrix + np.transpose(airport_reachability_matrix)

# Randomly selecting a subset of airports. We keep AMS and MIA as fixed hubs
# and randomly sample the others

n_A = 5

hubs     = ['AMS','MIA']
hubs     = sorted(hubs)
idx_hubs = [idx for idx,row in df_airports.iterrows() if row.IATA in hubs]

exit_cond = False
while exit_cond is False:
    subset_airports_idx   = list(set(df_airports.index.tolist())-set(idx_hubs))
    
    new_idx               = random.sample(subset_airports_idx, n_A-len(idx_hubs))
    idx_airports_instance = sorted(idx_hubs + new_idx)
    IATA_codes_instance   = [airports_IATA[i] for i in idx_airports_instance]
    
    airport_distance_matrix_red = airport_distance_matrix[np.ix_(
        idx_airports_instance, idx_airports_instance)]
    airport_reachability_matrix_red = airport_reachability_matrix[np.ix_(
        idx_airports_instance, idx_airports_instance)]
    
    G = ig.Graph(directed=True)
    
    # Add nodes
    for idx,airport in enumerate(IATA_codes_instance):
        G.add_vertex(idx=i) 
    
    # Add edges
    for i,airport_o in enumerate(IATA_codes_instance):
        for j,airport_d in enumerate(IATA_codes_instance):
            if j != i and airport_reachability_matrix_red[i][j] != 0:
            
                G.add_edge(source=i,target=j)
                
    # Check if Graph is its own giant component
    cl  = G.clusters()
    lcc = cl.giant()
    
    # Note: it should be the same if we test G.is_connected() directly and
    # check if the output is True
    if G.vcount()>lcc.vcount():
        pass
    else:
        exit_cond = True
    
df_airports_instance = df_airports.loc[idx_airports_instance]
df_airports_instance.to_excel(os.path.join(cwd,'airports_instance_%i.xlsx'%(ID_instance)),index=False)
df_airports_instance = df_airports_instance.reset_index(drop=True)
    
# Time matrix    
cruise_speed        = 850  # km/h
tol_time            = 30   # minutes
min_tat             = 2*60 # minutes
airport_time_matrix = np.zeros([len(df_airports_instance),len(df_airports_instance)])

for i,row_i in df_airports_instance.iterrows():
    for j,row_j in df_airports_instance.iterrows():
        if j > i:
            airport_time_matrix[i][j] = np.round(airport_distance_matrix_red[i][j]/cruise_speed*60+tol_time+min_tat,1) # minutes

airport_time_matrix     = airport_time_matrix+np.transpose(airport_time_matrix)

# Revise the time matrix and place a -1 in all (i,j) pairs that cannot be
# directly connected. We use the information from airport_reachability_matrix_red
# to do so 
for i,row_i in df_airports_instance.iterrows():
    for j,row_j in df_airports_instance.iterrows():
        if airport_reachability_matrix_red[i][j] == 0:
            airport_time_matrix[i][j] = -1

# Define all (i,j) pairs that are reachable via direct flight, 
# store the distance, the time, and the maximum payload transportable
# depending on the fleet type
OD_pairs = []
for i,row_i in df_airports_instance.iterrows():
    for j,row_j in df_airports_instance.iterrows():
         if airport_time_matrix[i][j] != -1 and (i,j) not in OD_pairs:
             OD_pairs.append((i,j))

OD_pairs_dict_ij_IATA = {od:(df_airports_instance.IATA[od[0]],df_airports_instance.IATA[od[1]]) for od in OD_pairs}        
OD_pairs_dict_IATA_ij = {v:k for k,v in OD_pairs_dict_ij_IATA.items()}

# Adding more info per (i,j) pair. For example, which aircraft type can 
# fly this route (note that there should be at least one, otherwise we 
# would not have defined this pair in the first place), and what is the
# maximum payload

OD_pairs_dict_ij_info = {k:[np.round(airport_distance_matrix_red[k[0]][k[1]],1),
                        airport_time_matrix[k[0]][k[1]],
                        {kk:np.round(compute_max_payload(PRD,kk,
                        np.round(airport_distance_matrix_red[k[0]][k[1]],1)),1) for kk in K.keys()}]
                        for k,v in OD_pairs_dict_ij_IATA.items()}

# Define for every (i,j) pair which aircraft type can fly that pair
OD_pairs_dict_ij_k_compatible = {od:[k for k in OD_pairs_dict_ij_info[od][2].keys() if
                                     OD_pairs_dict_ij_info[od][2][k] != -1] for od in
                                 OD_pairs_dict_ij_info.keys()}

# Define time-horizon and time-step of the problem
# Use thin information to compute how many time-steps it takes to
# fly each (i,j) route
T                = 4       # days
timespan         = T*24*60 # minutes
timestep         = 4*60    # minutes
timestamps       = [i*timestep for i in range(0,int(timespan/timestep+1))]
eps              = 0.1     # not used now, but might be used to use floor instead
                           # of ceiling if the flight arc only exceeds the node
                           # by eps*timestep or less

OD_pairs_dict_ij_timesteps = {k: int(np.floor(airport_time_matrix[k[0]][k[1]]/timestep))
                                 if np.mod(airport_time_matrix[k[0]][k[1]],timestep) <= eps else
                                 int(np.ceil(airport_time_matrix[k[0]][k[1]]/timestep))
                                 for k in OD_pairs_dict_ij_info.keys()}

# Adding minimum time from an airport to itself (0) to the previous 
# OD_pairs_dict_ij_timesteps dictionary because it is handier to use
# in some definitions and constraints below
for i,row_i in df_airports_instance.iterrows():
    OD_pairs_dict_ij_timesteps[(i,i)]=0
    
    

# Determine minimum number of time-steps it takes to go from any origin
# airport to any destination airport (the shortest path is computed using
# the time-steps from OD_pairs_dict_ij_timesteps)

G = ig.Graph(directed=True)

# Add nodes
nodes = list(set([item for t in OD_pairs_dict_ij_timesteps for item in t]))
for i in nodes:
    G.add_vertex(idx=i) 

# Add edges
for t in OD_pairs_dict_ij_timesteps.keys():
    G.add_edge(source=t[0],target=t[1],weight=OD_pairs_dict_ij_timesteps[t])
    
airport_shortest_path_timestep = np.zeros([len(df_airports_instance),len(df_airports_instance)])
for i in range(0,len(df_airports_instance)):
    for j in range(0,len(df_airports_instance)):
        if j != i:
            path = G.get_shortest_paths(i, j, weights=G.es['weight'], output="epath")
            distance = 0
            for e in path[0]:
                distance += G.es[e]['weight']
            airport_shortest_path_timestep[i][j] = distance

OD_minimum_timestep = {(i,j):int(airport_shortest_path_timestep[i][j]) 
                       for i in range(0,len(df_airports_instance)) for j
                       in range(0,len(df_airports_instance)) if j != i}

# Adding minimum time from an airport to itself (0) to the previous 
# OD_pairs_dict_ij_timesteps dictionary because it is handier to use
# in some definitions and constraints below
for i,row_i in df_airports_instance.iterrows():
    OD_minimum_timestep[(i,i)]=0            



# Creating nodes defining the Time-Space Network where aircraft can move
# We define 2 types of nodes:
# - activity nodes: i.e., node defining a specific airport at a specific 
#   moment in time
# - a source/sink node that is connected to every origin/
#   destination activity node of each airport. This node is used to 
#   allocate aircraft types to the most proper origin and destination for 
#   routing purposes

N = [(a,t) for a in IATA_codes_instance for t in timestamps]
N_dict_idx_at = {k:v for k,v in enumerate(N)}
N_dict_at_idx = {v:k for k,v in N_dict_idx_at.items()}

# Data on requests
Regions_OD_perc_commodity = {('North America','Latin America'):{'chemical':0.168,
                                                                'perishable':0.095,
                                                                'heavy':0.52,
                                                                'other':0.217},
                             ('Latin America','North America'):{'chemical':0.026,
                                                                'perishable':0.71,
                                                                'heavy':0.068,
                                                                'other':0.196},
                             ('Latin America','Europe'):{'chemical':0.035,
                                                                'perishable':0.794,
                                                                'heavy':0.068,
                                                                'other':0.098},
                             ('Europe','Latin America'):{'chemical':0.136,
                                                                'perishable':0.223,
                                                                'heavy':0.22,
                                                                'other':0.416},
                             ('North America','Europe'):{'chemical':0.20,
                                                                'perishable':0.05,
                                                                'heavy':0.49,
                                                                'other':0.26},
                             ('Europe','North America'):{'chemical':0.13,
                                                                'perishable':0.08,
                                                                'heavy':0.42,
                                                                'other':0.37},
                             ('Africa','Europe'):{'chemical':0.017,
                                                                'perishable':0.894,
                                                                'heavy':0.042,
                                                                'other':0.047},
                             ('Europe','Africa'):{'chemical':0.136,
                                                                'perishable':0.409,
                                                                'heavy':0.212,
                                                                'other':0.243},
                             ('Africa','North America'):{'chemical':0.017,
                                                                'perishable':0.894,
                                                                'heavy':0.042,
                                                                'other':0.047},
                             ('North America','Africa'):{'chemical':0.136,
                                                                'perishable':0.409,
                                                                'heavy':0.212,
                                                                'other':0.243},
                             ('North America','North America'):{'chemical':0.20,
                                                                'perishable':0.05,
                                                                'heavy':0.49,
                                                                'other':0.26},
                             ('Latin America','Latin America'):{'chemical':0.026,
                                                                'perishable':0.51,
                                                                'heavy':0.268,
                                                                'other':0.196},
                             }

request_characteristics_commodity_type = \
    {'chemical':{'weight':[0.4,0.8],'density':[0.15,0.25],
     'str_fct':[0.7,1.3],'perc_spec_ft':{'L':[1,0.6],
     'M':[0.5,0.6],'H':[0.25,0.25]}},
     'perishable':{'weight':[0.4,0.8],'density':[0.15,0.20],
     'str_fct':[1,1.3],'perc_spec_ft':{'L':[0.3,0.6],
     'M':[0.0,0.5],'H':[0,0.25]}},
     'heavy':{'weight':[0.4,0.8],'density':[0.5,0.7],
     'str_fct':[0.5,0.8],'perc_spec_ft':{'L':[0.4,0.8],
     'M':[0.2,0.3],'H':[0.1,0.1]}},
     'other':{'weight':[0.4,0.8],'density':[0.2,0.3],
     'str_fct':[0.9,1.1],'perc_spec_ft':{'L':[0.25,0.25],
     'M':[0,0],'H':[0,0]}},}
    
# Importing demand and cleaning a bit the dataframe
df_demand = pd.read_excel(os.path.join(cwd,'demand_matrix.xlsx'),index_col=False)
df_demand = df_demand.drop('Unnamed: 0', axis=1)
df_demand = df_demand.drop('Export', axis=1)
df_demand = df_demand.drop(len(df_demand)-1)

df_demand_instance = df_demand[list(df_airports_instance.IATA)]
df_demand_instance = df_demand_instance.loc[idx_airports_instance].reset_index(drop=True)

dict_IATA_idx = {k:v for v,k in enumerate(list(df_airports_instance.IATA))}
dict_idx_IATA = {v:k for k,v in dict_IATA_idx.items()}

# Normalizing remaining percentages to unitary value
demand_perc        = df_demand_instance.sum().sum()
df_demand_instance = df_demand_instance.applymap(lambda x: x*100/demand_perc/100)

# Define number of requests for the instance
n_R = 50

# Assign number of requests per (i,j) airport pair according to
# percentages defined before
dict_ODpair_requests = {(i,j):int(np.round(df_demand_instance.loc[dict_IATA_idx[i]][j]*n_R,0)) 
                        for i in dict_IATA_idx.keys() for j in 
                                    dict_IATA_idx.keys() if j != i}
# Define compatibility level
comp_level = 'M'

# Define time interval for release time and due date
T_e_rt = -0.25*timestamps[-1]
T_l_rt = 1/3*timestamps[-1]
T_rt   = [T_e_rt,T_l_rt]
T_e_dd = 1/2*timestamps[-1] 
T_l_dd = timestamps[-1]
T_dd   = [T_e_dd,T_l_dd]

R    = {}
cont = 0
for od in dict_ODpair_requests.keys():
    o   = od[0]
    d   = od[1]
    r_o = df_airports_instance[df_airports_instance.IATA == o].region.values[0]
    r_d = df_airports_instance[df_airports_instance.IATA == d].region.values[0]
    perc_comm = Regions_OD_perc_commodity[(r_o,r_d)]
    for i in range(0,dict_ODpair_requests[od]):
        rnd = random.random()
        if rnd <= perc_comm['chemical']:
            commodity_type = 'chemical'
        elif rnd <= perc_comm['chemical']+perc_comm['perishable']:
            commodity_type = 'perishable'
        elif rnd <= perc_comm['chemical']+perc_comm['perishable']+perc_comm['heavy']:
            commodity_type = 'heavy'
        else:
            commodity_type = 'other'
        
        t_rt = np.round(np.max([0,random.uniform(T_e_rt,T_l_rt)]),0)
        t_dd = np.round(np.max([random.uniform(T_e_dd,T_l_dd),t_rt+
                       OD_minimum_timestep[dict_IATA_idx[o],dict_IATA_idx[d]]]),0)
        
        weight_r  = np.round(random.uniform(request_characteristics_commodity_type[commodity_type]['weight'][0],
                    request_characteristics_commodity_type[commodity_type]['weight'][1]),1)
        volume_r  = np.round(weight_r/(random.uniform(request_characteristics_commodity_type[commodity_type]['density'][0],
                    request_characteristics_commodity_type[commodity_type]['density'][1])),1)
        str_fct_r = np.round(random.uniform(request_characteristics_commodity_type[commodity_type]['str_fct'][0],
                    request_characteristics_commodity_type[commodity_type]['str_fct'][1]),1)
        
        R[cont] = (o,d,r_o,r_d,commodity_type,weight_r,volume_r,str_fct_r,
                   1 if random.random() <= 
                   request_characteristics_commodity_type[commodity_type]['perc_spec_ft'][comp_level][0] else 0,
                   1 if random.random() <= 
                   request_characteristics_commodity_type[commodity_type]['perc_spec_ft'][comp_level][1] else 0,
                   t_rt,t_dd)
        cont += 1
        

# Define the incompatiblity sets

inc_combo = [('perishable','heavy'),('perishable','chemical')]

INC_dict  = {k:[(r1,r2) for idx_r1,r1 in enumerate(R.keys()) 
                        for idx_r2,r2 in enumerate(R.keys()) if (idx_r2>idx_r1
                        and ((R[r1][4]==k[0] and R[r2][4]==k[1]) or
                             (R[r1][4]==k[1] and R[r2][4]==k[0])))] for k in inc_combo}




        
# Definition of ULD types
n_spec_feat = 2

V_info      = {0:[1.2,4,1,0], # LD3,     weight [ton], volume [m^3], 1 if hazardous, 1 if temp. controlled
               1:[1.2,4,1,1], # LD3plus, weight [ton], volume [m^3], 1 if hazardous, 1 if temp. controlled
               2:[4.2,8,0,0], # LD7,     weight [ton], volume [m^3], 1 if hazardous, 1 if temp. controlled
               3:[4.2,8,1,1]} # LD7plus, weight [ton], volume [m^3], 1 if hazardous, 1 if temp. controlled

# Aircraft characteristics
K_info = {0:[10.4,1,440,2,2,14,6], # operational cost [Euro/km], weight [ton], volume [m^3], #LD3, #LD3plus, #LD7, #LD7plus
          1:[9.0,1,440,4,14,12,0]} # operational cost [Euro/km], weight [ton], volume [m^3], #LD3, #LD3plus, #LD7, #LD7plus

# Define all ground arcs
G = [(i,i+1) for i in range(0,len(N_dict_idx_at)-1) if N_dict_idx_at[i][0]==N_dict_idx_at[i+1][0]]

# Define all flight arcs
F = [(i,j) for i in N_dict_idx_at.keys() for j in N_dict_idx_at.keys() for od in OD_pairs
           if (N_dict_idx_at[i][0]==dict_idx_IATA[od[0]] and N_dict_idx_at[j][0]==dict_idx_IATA[od[1]] and 
           (N_dict_idx_at[j][1]-N_dict_idx_at[i][1]) == OD_pairs_dict_ij_timesteps[(dict_IATA_idx[N_dict_idx_at[i][0]],
           dict_IATA_idx[N_dict_idx_at[j][0]])]*timestep and
           N_dict_idx_at[j][1] <= timespan)]

def comp_ULD(r,V_info,ULD_type,n_spec_feat):
    comp_features = [1 if V_info[ULD_type][2+i]>=r[8+i] else 0 for i in range(0,n_spec_feat)]
    return all([ c==1 for c in comp_features])

# Defining the full set of ULDs that we can inject into the system
U = [[((r[0],int(np.ceil(r[10]/timestep)*timestep)),((r[1]),int(np.floor(r[11]/timestep)*timestep))),
      (N_dict_at_idx[(r[0],int(np.ceil(r[10]/timestep)*timestep))],N_dict_at_idx[((r[1]),int(np.floor(r[11]/timestep)*timestep))]),u,idx_r] for idx_r,r in R.items()
     for u in V_info.keys() if comp_ULD(r,V_info,u,n_spec_feat)] 
U_dict = {k:v for k,v in enumerate(U)}

# Defining the subset of ground arcs that each ULD can use. We omit for now 
# ground arcs whose origin is before the release time of the ULD and 
# ground arcs whose destination is after the due date of the ULD 
G_u_tup = {k:[g for g in G if (N_dict_idx_at[g[0]][1]>=U_dict[k][0][0][1] and N_dict_idx_at[g[1]][1]<=U_dict[k][0][1][1])]
          for k in U_dict.keys()}

# Defining the subset of flight arcs that each ULD can use. For now, we simply
# cut-off the flight arcs that are outside the time-range of the ULD, but we could
# even disregard more flight arcs (e.g., flight arcs starting at the release time
# of the ULD from airports that are not the origin airport, because the ULD cannot
# physically be there in such a short time).
F_u_tup = {k:[f for f in F if (N_dict_idx_at[f[0]][1]>=U_dict[k][0][0][1] and N_dict_idx_at[f[1]][1]<=U_dict[k][0][1][1])]
          for k in U_dict.keys()}

G_u_tup_incomp = {u:[g for g in G_u_tup[u] if (((N_dict_idx_at[g[1]][1]+
                      OD_minimum_timestep[(dict_IATA_idx[N_dict_idx_at[g[1]][0]],
                                           dict_IATA_idx[u_values[0][1][0]])]*timestep)>
                      u_values[0][1][1]) or 
                      (N_dict_idx_at[g[0]][1]-
                      OD_minimum_timestep[(dict_IATA_idx[u_values[0][0][0]],
                                           dict_IATA_idx[N_dict_idx_at[g[0]][0]])]*timestep<
                      u_values[0][0][1]))] for u,u_values in U_dict.items()}

# Removing for each ULD two sets of flight arcs: (i) flight arcs from the 
# origin airport that depart too late to ensure the ULD arrives at the sink 
# node in time and (ii) flight arcs arriving to the destination airport
# too early and that would imply the ULD must leave before the release time

F_u_tup_incomp = {u:[f for f in F_u_tup[u] if (((N_dict_idx_at[f[1]][1]+
                      OD_minimum_timestep[(dict_IATA_idx[N_dict_idx_at[f[1]][0]],
                                           dict_IATA_idx[u_values[0][1][0]])]*timestep)>
                      u_values[0][1][1]) or 
                      (N_dict_idx_at[f[0]][1]-
                      OD_minimum_timestep[(dict_IATA_idx[u_values[0][0][0]],
                                           dict_IATA_idx[N_dict_idx_at[f[0]][0]])]*timestep<
                      u_values[0][0][1]))] 
                   for u,u_values in U_dict.items()} 

# Re-defining F_u so that we get rid of the incompatible ground arcs
# computed above
G_u_tup = {u:list(set(g)-set(G_u_tup_incomp[u])) for u,g in G_u_tup.items()}

# Re-defining F_u so that we get rid of the incompatible flight arcs
# computed above
F_u_tup = {u:list(set(f)-set(F_u_tup_incomp[u])) for u,f in F_u_tup.items()}
  

# For each request, define the (source,sink) nodes where it should enter/exit
# the TSN if transported
R_dict_source_sink = {r:(N_dict_at_idx[(v[0],int(np.ceil(v[10]/timestep)*timestep))],
                         N_dict_at_idx[((v[1]),int(np.floor(v[11]/timestep)*timestep))]) for r,v in R.items()}

# For each request, determine the ULDs that can transport it. The choice is
# made based on the following criteria:
# - origin and destination airports should match
# - if the ULD leaves immediately, it can arrive at the destination airport
#   before the due date of the request
# - the ULD type should be compatible with the request characteristics
U_r = {r:[u for u,u_values in U_dict.items() if u_values[0][0][0]==r_values[0] and 
          u_values[0][1][0]==r_values[1] and
          u_values[0][0][1] + 
          OD_minimum_timestep[(dict_IATA_idx[u_values[0][0][0]],dict_IATA_idx[u_values[0][1][0]])]*timestep
          <= N_dict_idx_at[R_dict_source_sink[r][1]][1] and # if the ULD travels as soon as possible, it will arrive before the due date of the request
          comp_ULD(r_values,V_info,u_values[2],n_spec_feat)] for r,r_values in R.items()}

# For each ULD, define the subset of requests that can be transported in that ULD
R_u = {u:[r for r,r_values in U_r.items() if u in r_values] for u,u_values in U_dict.items()}



# For each ULD, determine the flight arcs that it can use to leave the origin
# airport and the flight arcs that it can use to get to the destination airport
F_orig_u = {u:[f for f in F_u_tup[u] if N_dict_idx_at[f[0]][0] == u_values[0][0][0]] for u,u_values in U_dict.items()}       
F_dest_u = {u:[f for f in F_u_tup[u] if N_dict_idx_at[f[1]][0] == u_values[0][1][0]] for u,u_values in U_dict.items()}



# Numbering all nodes of the TSN
N_dict = {k:v for k,v in enumerate(N)}

# Adding all source nodes of ULDs, and mapping each ULD with the index of the
# associated source node
ULD_source_dict  = {int(k+len(N_dict)):v[0][0] for k,v in U_dict.items()}
U_to_source_dict = {idx:k for idx,k in enumerate(ULD_source_dict.keys())}     

# Adding all sink nodes of ULDs, and mapping each ULD with the index of the
# associated sink node
ULD_sink_dict = {int(k+len(N_dict)+len(ULD_source_dict)):v[0][1] for k,v in U_dict.items()}
U_to_sink_dict = {idx:k for idx,k in enumerate(ULD_sink_dict.keys())} 

# Additional source/sink nodes where all aircraft are initially stationed and need to finish 
# their journey as part of the fleet assignment problem
N_dummy_source = {int(len(N_dict)+len(ULD_source_dict)+len(ULD_sink_dict)):('dummy_source',timestamps[0])}
N_dummy_sink   = {int(len(N_dict)+len(ULD_source_dict)+len(ULD_sink_dict)+len(N_dummy_source)):('dummy_sink',timestamps[-1])}

N_all_dict = {**N_dict,**ULD_source_dict,**ULD_sink_dict,**N_dummy_source,**N_dummy_sink}



# Giving indexes to ground and flight arcs
G_dict = {k:v for k,v in enumerate(G)}
F_dict = {int(k+len(G_dict)):v for k,v in enumerate(F)}

#F_u_idx = {u:[k for k,v in F_dict.items() for f in F_u[u] if v == f]
#           for u in F_u.keys()}

# Defining arcs from each ULD source to the first node in the TSN available
ULD_source_TSN_dict = {int(k+len(G_dict)+len(F_dict)):(U_to_source_dict[k],U_dict[k][1][0])
                     for k in U_dict.keys()}  

# Defining arcs from the last node in the TSN available to each ULD sink node
TSN_ULD_sink_dict   = {int(k+len(G_dict)+len(F_dict)+len(ULD_source_TSN_dict)):
                       (U_dict[k][1][1],U_to_sink_dict[k])
                       for k in U_dict.keys()}  

# Defining arcs from dummy source node to origin nodes (t=0) in the TSN
dummy_source_TSN = {int(idx_1+idx_2+len(G_dict)+len(F_dict)+len(ULD_source_TSN_dict)
                        +len(TSN_ULD_sink_dict)):(k,N_dict_at_idx[(airport,timestamps[0])]) for idx_1,k in enumerate(N_dummy_source.keys()) 
                    for idx_2,airport in enumerate(dict_idx_IATA.values())}

# Defining arcs from destination nodes (t=timespan) in the TSN to dummy sink
TSN_dummy_sink = {int(idx_1+idx_2+len(G_dict)+len(F_dict)+len(ULD_source_TSN_dict)
                        +len(TSN_ULD_sink_dict)+len(dummy_source_TSN)):(N_dict_at_idx[(airport,timestamps[-1])],k) for idx_1,k in enumerate(N_dummy_sink.keys()) 
                    for idx_2,airport in enumerate(dict_idx_IATA.values())}

# Defining bypass arc from dummy source to dummy sink
dummy_source_dummy_sink = {int(len(G_dict)+len(F_dict)+len(ULD_source_TSN_dict)
                        +len(TSN_ULD_sink_dict)+
                        len(dummy_source_TSN)+len(TSN_dummy_sink)):
                            ([k for k,v in N_all_dict.items() if v[0]=='dummy_source'][0],
                             [k for k,v in N_all_dict.items() if v[0]=='dummy_sink'][0])}
    
A_all_dict = {**G_dict,**F_dict,**ULD_source_TSN_dict,**TSN_ULD_sink_dict,
              **dummy_source_TSN,**TSN_dummy_sink,**dummy_source_dummy_sink}

# Subset of arcs that aircraft can use
A_K_dict       = {**G_dict,**F_dict,
                  **dummy_source_TSN,**TSN_dummy_sink,**dummy_source_dummy_sink}
A_K_dict_a_idx = {v:k for k,v in A_K_dict.items()}

# Subset of arcs that ULDs can use
A_U_dict       = {**G_dict,**F_dict,**ULD_source_TSN_dict,**TSN_ULD_sink_dict}
A_U_dict_a_idx = {v:k for k,v in A_U_dict.items()}

# For all types of arcs, get the indices. This will be useful when writing 
# constraints later
G_arcs_idxs                  = list(G_dict.keys()) 
F_arcs_idxs                  = list(F_dict.keys()) 
ULD_source_TSN_arcs_idxs     = list(ULD_source_TSN_dict.keys()) 
TSN_ULD_sink_arcs_idxs       = list(TSN_ULD_sink_dict.keys()) 
dummy_source_TSN_arcs_idxs   = list(dummy_source_TSN.keys()) 
TSN_dummy_sink_arcs_idxs     = list(TSN_dummy_sink.keys())  
dummy_source_dummy_sink_idxs = list(dummy_source_dummy_sink.keys())

ULD_source_TSN_u_a_dict      = {idx_u:u for idx_u,u in enumerate(ULD_source_TSN_dict.keys())}
TSN_ULD_sink_u_a_dict        = {idx_u:u for idx_u,u in enumerate(TSN_ULD_sink_dict.keys())}

# For the flight arcs, define for a dictionary where the index is the index
# of the current flight arc, and the key is the subset of aircraft
# types that can transverse that arc. We retrieve this information from the
# OD_pairs_dict_ij_k_compatible dictionary that we previously computed

K_f = {f:OD_pairs_dict_ij_k_compatible[(dict_IATA_idx[N_dict_idx_at[F_dict[f][0]][0]],
                                      dict_IATA_idx[N_dict_idx_at[F_dict[f][1]][0]])] for f in F_arcs_idxs}


# Define subset of ground arcs that a specific ULD can use
G_u = {u:[A_U_dict_a_idx[a] for a in G_u_tup[u]] for u in U_dict.keys()}

F_u = {u:[A_U_dict_a_idx[a] for a in F_u_tup[u]] for u in U_dict.keys()}

# For each ULD, define the subset of arcs that can be used
AU_u = {u:G_u[u]+F_u[u]+[ULD_source_TSN_u_a_dict[u]]+
        [TSN_ULD_sink_u_a_dict[u]] for u in U_dict.keys()}


# For nodes of the original TSN, define the two subsets Delta_plus and 
# Delta_minus (resp., the subset of arcs arriving to or leaving from the
# current node). Note that these subsets are different for aircraft and
# ULDs as they share some arcs, but are also characterized by
# unique arcs that only aircraft/ULDs can transverse

# Subsets for aircraft. Here we need two indices because we need
# conservation of flow per node and per aircraft type
Delta_plus_K  = {(k,n):[a for a,v in A_K_dict.items() if (a not in F_arcs_idxs and n==v[1])
                        or (a in F_arcs_idxs and k in K_f[a] and n==v[1])]
                        for k in K for n in N_dict.keys()}
Delta_minus_K = {(k,n):[a for a,v in A_K_dict.items() if (a not in F_arcs_idxs and n==v[0])
                        or (a in F_arcs_idxs and k in K_f[a] and n==v[0])]
                        for k in K for n in N_dict.keys()}

# Subset for ULDs
Delta_plus_U  = {(u,n):[a for a in AU_u[u] if n==A_all_dict[a][1]]
                        for u in U_dict.keys() for n in N_dict.keys()}
Delta_minus_U = {(u,n):[a for a in AU_u[u] if n==A_all_dict[a][0]]
                        for u in U_dict.keys() for n in N_dict.keys()}



# Define subset of ULDs of type v
U_v = {k:[u for u,u_info in U_dict.items() if u_info[2]==k] for k in V_info.keys()}



# Define subset of ULDs that can use a specific flight arc
U_f = {f:[u for u in U_dict.keys() if f in F_u[u]] for f in F_dict.keys()}



# Define subset of ULDs of a specific type that can use a specific flight arc
U_vf = {(v,f):[u for u in U_f[f] if U_dict[u][2]==v] for v in V_info.keys() for f in F_dict.keys()}



# Define for each flight arc some properties (e.g.,max payload according to
# fleet type)

F_info = {f:OD_pairs_dict_ij_info[(dict_IATA_idx[N_dict_idx_at[F_dict[f][0]][0]],
                                   dict_IATA_idx[N_dict_idx_at[F_dict[f][1]][0]])]
          for f in F_dict.keys()}

W_fk = {(f,k):F_info[f][2][k] for f in F_dict.keys() for k in K_f[f]}



# def u1_u2_dominance(U_dict,u1,u2):
#     features_u1    = V_info[U_dict[u1][2]][2:]
#     features_u2    = V_info[U_dict[u2][2]][2:]
#     delta_features = [a_i - b_i for a_i, b_i in zip(features_u1,features_u2)]
#     if min(delta_features)>=0:
#         dominance = True
#     else:
#         dominance = False
    
#     return dominance

# V_types     = {'LD-3':(0,1),
#                'LD-7':(2,3)}
# V_type_idx    = {u:[t for t,t_info in V_types.items() if u_info[2] in t_info] for u,u_info in U_dict.items()}
# V_type_ULDidx = {u:[j for j,j_info in U_dict.items() if j!= u and
#                     V_type_idx[j]==V_type_idx[u]] for u,u_info in U_dict.items()} 

# U_dominance = {u:[j for j in V_type_ULDidx[u] if 
#                   U_dict[j][0][0][1]<=U_dict[u][0][0][1] and
#                   U_dict[j][0][1][1]>=U_dict[u][0][1][1] and
#                   u1_u2_dominance(U_dict,u,j) is True] 
#                 for u,u_info in U_dict.items()}

# Defining subsets F_ruO and F_ruD that define respectively
# F_ruO: set of flight arcs that ULD u can use to depart from the origin
# airport later than the release time of the request
# F_ruD: set of flight arcs that ULD u can use to arrive at the destination
# airport sooner than the due date of the request

F_ruO = {(r,u):[f for f in F_u[u] if ((dict_IATA_idx[N_dict_idx_at[F_dict[f][0]][0]]==
                dict_IATA_idx[R[r][0]]) and 
                (N_dict_idx_at[F_dict[f][0]][1]>=R[r][10]))] for r in R.keys() for u in U_r[r]}

F_ruD = {(r,u):[f for f in F_u[u] if ((dict_IATA_idx[N_dict_idx_at[F_dict[f][1]][0]]==
                dict_IATA_idx[R[r][1]]) and 
                (N_dict_idx_at[F_dict[f][1]][1]<=R[r][11]))] for r in R.keys() for u in U_r[r]}



###########################################
### Defining now the optimization model ###
###########################################

# Setup model
model = Model()

# Decision variables

x = {} # aircraft fleet routing decision variables
y = {} # ULD routing decision variables
z = {} # Request to ULD assignment decision variables
w = {}

# Aircraft routing decision variables for ground arcs (integer)
for g in G_dict.keys():
    for k,v in K.items():
        x[g,k] = model.addVar(lb=0, ub=v[0], vtype=GRB.INTEGER, name="x_%s_%s"%(g,k))

# Aircraft routing decision variables for flight arcs (binary)
for f in F_dict.keys():
    for k in K_f[f]:
        x[f,k] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name="x_%s_%s"%(f,k))
        
# Aircraft routing decision variables from dummy source to TSN (integer)
for a in dummy_source_TSN.keys():
    for k,v in K.items():
        x[a,k] = model.addVar(lb=0, ub=v[0], vtype=GRB.INTEGER, name="x_%s_%s"%(a,k))
        
# Aircraft routing decision variables from TSN to dummy sink (integer) 
for a in TSN_dummy_sink.keys():
    for k,v in K.items():
        x[a,k] = model.addVar(lb=0, ub=v[0], vtype=GRB.INTEGER, name="x_%s_%s"%(a,k)) 
        
# Aircraft routing decision variable from dummy source to dummy sink (integer)
for k,v in K.items():
    for a in dummy_source_dummy_sink.keys():
        x[a,k] = model.addVar(lb=0, ub=v[0], vtype=GRB.INTEGER, name="x_%s_%s"%(a,k)) 
        
# ULD routing decision variables from source node to TSN node
for idx,a in enumerate(ULD_source_TSN_dict.keys()):
    y[a,idx] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name="y_%s_%s"%(a,idx))
    
# ULD routing decision variables from TSN node to sink node
for idx,a in enumerate(TSN_ULD_sink_dict.keys()):
    y[a,idx] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name="y_%s_%s"%(a,idx))

# ULD routing decision variables for ground arcs
for u in U_dict.keys():
    for g in G_u[u]:
        y[g,u] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name="y_%s_%s"%(g,u))

# ULD routing decision variables for flight arcs        
for u in U_dict.keys():
    for f in F_u[u]:
        y[f,u] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name="y_%s_%s"%(f,u))

# Request to ULD assignment decision variables        
for r in R.keys():
    for u in U_r[r]:
        z[r,u] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name="z_%s_%s"%(r,u))
        
# Linearization of y*z decision variables
for r in R.keys():
    for u in U_r[r]:
        for f in F_u[u]:
            w[f,u,r] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name="w_%s_%s_%s"%(f,u,r))


###################
### Constraints ###
###################

# Every flight arc can be flown at most by one aircraft
C1 = model.addConstrs((quicksum(x[f,k] for k in K_f[f])<=1 for f in F_dict.keys()), 
                  name="C1")

# For each flight leg, we can carry as many ULDs of type v as they are
# allowed by the configuration
C2 = model.addConstrs((quicksum(y[f,u] for u in U_vf[(v,f)])-
                  quicksum(K_info[k][v+3]*x[f,k] for k in K_f[f])<=0 
                  for f in F_dict.keys() for v in V_info.keys()),
                  name="C2")

# For each ULD, we must satisfy the weight capacity
C3 = model.addConstrs((quicksum(R[r][5]*z[r,u] for r in R_u[u])<=
                  V_info[U_dict[u][2]][0] for u in U_dict.keys()),
                  name="C3")


# For each ULD, we must satisfy the volume capacity
C4 = model.addConstrs((quicksum(R[r][6]*z[r,u] for r in R_u[u])<=
                  V_info[U_dict[u][2]][1] for u in U_dict.keys()),
                  name="C4")



# Each request can be assigned to at most one ULD
C5 = model.addConstrs((quicksum(z[r,u] for u in U_r[r])<=
                  1 for r in R.keys()),
                  name="C5")


# The overall number of aircraft of a specific type must leave the
# dummy source
C6 = model.addConstrs(((quicksum(x[a,k] for a in dummy_source_TSN.keys())+\
                        quicksum(x[a,k] for a in dummy_source_dummy_sink.keys())==
                        K[k][0] for k in K.keys())),name="C6")
    

# The overall number of aircraft of a specific type must arrive to the
# dummy sink

C7 = model.addConstrs(((quicksum(x[a,k] for a in TSN_dummy_sink.keys())+\
                        quicksum(x[a,k] for a in dummy_source_dummy_sink.keys())==
                        K[k][0] for k in K.keys())),name="C7")


# Conservation of flow in the TSN per aircraft type

C8 = model.addConstrs((quicksum(x[a,k] for a in Delta_plus_K[(k,n)])-
                        quicksum(x[a,k] for a in Delta_minus_K[(k,n)])==0 
                        for k in K.keys() for n in N_dict.keys()),name="C8")



# Conservation of flow in the TSN per ULD

C9 = model.addConstrs((quicksum(y[a,u] for a in Delta_plus_U[(u,n)])-
                        quicksum(y[a,u] for a in Delta_minus_U[(u,n)])==0 
                        for u in U_dict.keys() for n in N_dict.keys()),name="C9")



# A request can be assigned to a ULD if that ULD leaves after the release time
# of the request, and a request can be assigned to a ULD if that ULD arrives 
# before the due date of the request

C14 = model.addConstrs((z[r,u]-
                        quicksum(y[f,u] for f in F_ruO[r,u])<=0 
                        for r in R.keys() for u in U_r[r]),name="C14")


C15 = model.addConstrs((z[r,u]-
                        quicksum(y[f,u] for f in F_ruD[r,u])<=0 
                        for r in R.keys() for u in U_r[r]),name="C15")



# Incompatibility constraints
if comp_level != "H":
    C16 = model.addConstrs((z[r[0],u]+z[r[1],u]<=1) 
          for inc in INC_dict.keys() for r in INC_dict[inc] 
          for u in list(set(U_r[r[0]])&set(U_r[r[1]])))



#################################
### Define objective function ###
#################################

obj = LinExpr()

# Operational cost due to routing of aircraft fleet
for f in F_dict.keys():
    for k in K_f[f]:
        obj -= K_info[k][0]*F_info[f][0]/10*x[f,k]

# Operational cost due to routing of ULDs
C_ULD = .1
for u in U_dict.keys():
    for f in F_u[u]:
        obj -= C_ULD*F_info[f][0]*y[f,u]

# Revenue due to transporting requests
R_avg = 4000 # Euros/ton
for r in R.keys():
    for u in U_r[r]:
        obj += R_avg*R[r][7]*R[r][5]*z[r,u]

# Add a small cost to enter the TSN from the dummy source
# to avoid symmetries
eps = 0.01
for a in dummy_source_TSN.keys():
    for k,v in K.items():
        obj -= eps*x[a,k]




model.setObjective(obj,GRB.MAXIMIZE)
model.update()
model.write("full_arc_based.lp")  

#%%

# Defining callback function
def callback_lazyConstrs(model, where):
  
  if where== GRB.Callback.MIPSOL:
    # Get the current solution
    x_val = model.cbGetSolution(x)
    y_val = model.cbGetSolution(y)
    z_val = model.cbGetSolution(z)
    
    fk_used = [k for k,v in x_val.items() if v>=0.99 and k[0] in F_arcs_idxs]
    # For every used arc, check if payload capacity is not exceeded
    for fk in fk_used:
        f       = fk[0] # flight arc
        k       = fk[1] # aircraft type
        u_f     = [k[1] for k,v in y_val.items() if v>=0.99 and k[0] == f] # All ULDs using that flight arc
        r_u     = {u:[k[0] for k,v in z_val.items() if v>=0.99 and k[1]==u] for u in u_f}
        Payload = sum([R[k[0]][5] for k,v in z_val.items() 
                             if v>=0.99 and k[1] in u_f]) # Weight of all requests carried along that flght arc
        # If payload capacity is exceeded, add lazy constraint
        if Payload > W_fk[(f,k)]:
            print('Lazy constraint is added!')
             
            for u in u_f:
                for r in r_u[u]:
                    model.cbLazy(y[f,u]+z[r,u]-w[f,u,r]<=1)
            
            for u in u_f:
                for r in r_u[u]:
                    model.cbLazy(w[f,u,r]-y[f,u]<=0) 
                                    
            for u in u_f:
                for r in r_u[u]:
                    model.cbLazy(w[f,u,r]-z[r,u]<=0) 
                                    
            
            model.cbLazy(quicksum(R[r][5]*w[f,u,r] for u in u_f for r in r_u[u])-
                            W_fk[(f,k)]*x[f,k]<=0)
        
        
    

#%%

# Solve
model.setParam('MIPGap',0.001)
model.setParam('TimeLimit',2*3600) # seconds
model.setParam("LogFile","full_arc_based.log")
#model.Params.LogToConsole = 0
model.Params.lazyConstraints = 1
model.optimize(callback_lazyConstrs) 

solution = []

# Retrieve variable names and values
for v in model.getVars():
    solution.append([v.varName,v.x])

# Retrieve active routing variables
active_variables = []
for i in range(0,len(solution)):
    if solution[i][1] >= 0.99:
        active_variables.append([solution[i][0],solution[i][1]])


        
# Store routing decision variables
x_variables = [(int(v[0][[x for x,char in enumerate(v[0]) if char=="_"][0]+1:[x for x,char in enumerate(v[0]) if char=="_"][1]]),
                int(v[0][[x for x,char in enumerate(v[0]) if char=="_"][1]+1:]))
                for v in active_variables if v[0][0]=="x"]

x_variables_dict = {k:[a[0] for a in x_variables if a[1]==k] for k in K.keys()}

F_k_sol          = {k:[x for x in x_variables_dict[k] if x in F_dict.keys()]
                    for k in K.keys()}



F_k_sol_tuple = {k:[(N_dict_idx_at[F_dict[f][0]],N_dict_idx_at[F_dict[f][1]]) 
                    for f in F_k_sol[k]]
                    for k in K.keys()}

F_k_sol_tuple_srt = {k:sorted(F_k_sol_tuple[k], key = lambda x: x[0][1])}