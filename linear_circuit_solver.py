import pandas as pd
import numpy as np

def handle_submit(circuit_data):
    gnd = circuit_data.pop('ground_node', None)
    df = pd.DataFrame(circuit_data['elements'])
    df['start'] = df['coordinates'].apply(lambda x: tuple(x[:2]))
    df['end'] = df['coordinates'].apply(lambda x: tuple(x[2:]))
    df = df.drop('coordinates', axis=1)

    df = df.set_index('number')
    df = df.sort_index()
    node_list = set(df['start'].tolist() + df['end'].tolist())

    node_df = pd.DataFrame(list(node_list), columns=['x', 'y'])
    node_df = pd.concat([node_df[node_df.apply(tuple, axis=1) == gnd], 
                         node_df[node_df.apply(tuple, axis=1) != gnd]]).reset_index(drop=True)    
    node_df.index.name = 'node_index'
    
    coord_to_index = dict(zip(node_df.apply(tuple, axis=1), node_df.index))
    df['start_node'] = df['start'].map(coord_to_index)
    df['end_node'] = df['end'].map(coord_to_index)
    n_nodes = len(node_df)-1
    
    voltage_sources = df[df['type'] == 'voltage source'].copy()
    voltage_sources['value'] = voltage_sources['value'].astype(float)
    voltage_sources = voltage_sources[['value', 'start_node', 'end_node']]
    voltage_sources['index'] = range(1,len(voltage_sources)+1)
    n_voltage_sources = len(voltage_sources)
    
    current_sources = df[df['type'] == 'current source'].copy()
    current_sources['value'] = current_sources['value'].astype(float)
    current_sources = current_sources[['value', 'start_node', 'end_node']]
    current_sources['index'] = range(1,len(current_sources)+1)
    n_current_sources = len(current_sources)

    conductance = df[df['type'] == 'resistor'].copy()
    conductance['value'] = 1/conductance['value'].astype(float)
    conductance = conductance[['value','start_node','end_node']]
    conductance['index'] = range(1,len(conductance)+1)
    n_conductance = len(conductance)
    
    B = np.zeros((n_nodes,n_voltage_sources))
    G = np.zeros((n_nodes,n_nodes))
    D = np.zeros((n_voltage_sources, n_voltage_sources))

    for i in range(1,n_conductance+1):
        row1 = conductance[conductance['index'] == i]
        start_node = row1['start_node'].iloc[0]
        end_node = row1['end_node'].iloc[0]
        if(start_node!=0 and end_node!=0):
            G[start_node-1][end_node-1] = -row1['value'].iloc[0]
            G[end_node-1][start_node-1] = -row1['value'].iloc[0]
        elif(start_node==0):
            G[end_node-1][end_node-1] = row1['value'].iloc[0]
        elif(end_node==0):
            G[start_node-1][start_node-1] = row1['value'].iloc[0]
            
    for i in range(n_nodes):
        for j in range(n_nodes):
            if(i!=j): G[i][i] += -G[i][j]
            
    for i in range(1,n_voltage_sources+1):
        row1 = voltage_sources[voltage_sources['index'] == i]
        start_node = row1['start_node'].iloc[0]
        end_node = row1['end_node'].iloc[0]
        row2 = df[df['start_node'] == start_node]
        row3 = row2[row2['end_node'] == end_node]
        start_coords = row3['start'].iloc[0]
        end_coords = row3['end'].iloc[0]
        
        if(row3['start_node'].iloc[0]!=0 and row3['end_node'].iloc[0]!=0):
            if(start_coords[0]>end_coords[0] or start_coords[1]<end_coords[1]):
                B[row3['start_node'].iloc[0]-1][i-1]=1
                B[row3['end_node'].iloc[0]-1][i-1]=-1
            elif(start_coords[0]<end_coords[0] or start_coords[1]>end_coords[1]):
                B[row3['start_node'].iloc[0]-1][i-1]=-1
                B[row3['end_node'].iloc[0]-1][i-1]=1
                
        elif(row3['start_node'].iloc[0]==0):
            if(start_coords[0]>end_coords[0] or start_coords[1]<end_coords[1]):
                B[row3['end_node'].iloc[0]-1][i-1]=-1
            elif(start_coords[0]<end_coords[0] or start_coords[1]>end_coords[1]):
                B[row3['end_node'].iloc[0]-1][i-1]=1

        elif(row3['end_node'].iloc[0]==0):
            if(start_coords[0]>end_coords[0] or start_coords[1]<end_coords[1]):
                B[row3['start_node'].iloc[0]-1][i-1]=1
            elif(start_coords[0]<end_coords[0] or start_coords[1]>end_coords[1]):
                B[row3['start_node'].iloc[0]-1][i-1]=-1
                
    C = B.transpose()    
    A = np.bmat([[G, B], [C, D]])    
    z = np.zeros((n_voltage_sources+n_nodes,1))
    
    for i in range(n_voltage_sources):
        row1 = voltage_sources[voltage_sources['index'] == i+1]
        z[i+n_nodes][0] = row1['value'].iloc[0]

    for i in range(1,n_current_sources+1):
        row1 = current_sources[current_sources['index'] == i]
        value = row1['value'].iloc[0].astype(float)
        start_node = row1['start_node'].iloc[0]
        end_node = row1['end_node'].iloc[0]
        row2 = df[df['start_node'] == start_node]
        row3 = row2[row2['end_node'] == end_node]
        start_coords = row3['start'].iloc[0]
        end_coords = row3['end'].iloc[0]
        
        if(row3['start_node'].iloc[0]!=0 and row3['end_node'].iloc[0]!=0):
            if(start_coords[0]>end_coords[0] or start_coords[1]<end_coords[1]):
                z[row3['start_node'].iloc[0]-1][0]+=value
                z[row3['end_node'].iloc[0]-1][0]+=-value
            elif(start_coords[0]<end_coords[0] or start_coords[1]>end_coords[1]):
                z[row3['start_node'].iloc[0]-1][0]+=-value
                z[row3['end_node'].iloc[0]-1][0]+=value
                
        elif(row3['start_node'].iloc[0]==0):
            if(start_coords[0]>end_coords[0] or start_coords[1]<end_coords[1]):
                z[row3['end_node'].iloc[0]-1][0]+=-value
            elif(start_coords[0]<end_coords[0] or start_coords[1]>end_coords[1]):
                z[row3['end_node'].iloc[0]-1][0]+=value

        elif(row3['end_node'].iloc[0]==0):
            if(start_coords[0]>end_coords[0] or start_coords[1]<end_coords[1]):
                z[row3['start_node'].iloc[0]-1][0]+=value
            elif(start_coords[0]<end_coords[0] or start_coords[1]>end_coords[1]):
                z[row3['start_node'].iloc[0]-1][0]+=-value
                
    x = np.linalg.solve(A,z)    
    print(df)
    print(node_df)
    print(voltage_sources)
    print(current_sources)
    print(A)
    print(z)
    print(x)
