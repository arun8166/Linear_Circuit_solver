import tkinter as tk
from solver_gui import GridGUI
import pandas as pd
import numpy as np

def main():
    root = tk.Tk()
    root.title("Interactive Grid")
    root.geometry("600x400")
    
    grid_gui = GridGUI(root)
    root.mainloop()

    components = grid_gui.component_vars
    ground = grid_gui.gnd
    ground_node = ground[::-1]
    print(ground_node)
    data = []
    for (row1, col1, row2, col2), component in components.items():
        data.append({
            'start_node': (col1,row1),
            'end_node': (col2,row2),
            'type': component['type'],
            'value': component['value']
        })
    df = pd.DataFrame(data)
    var1=df['start_node'].values.tolist()
    var2=df['end_node'].values.tolist()     
    node_list = list(set(var1+var2))
    node_list.remove(ground_node)
    
    
    nodes = pd.DataFrame(node_list,columns=['node'])
    nodes['node_number']=nodes.index+1
    n_nodes=len(nodes)
        
    vsource = df[df['type'] == 'Voltage Source'][['start_node', 'end_node', 'value']]
    vsource['vsource_number']=vsource.index+1
    n_vsource=len(vsource)

    resistance = df[df['type'] == 'Resistance'][['start_node', 'end_node', 'value']]
    conductance = resistance
    conductance['value'] = 1/resistance['value']
    
    isource = df[df['type'] == 'Current Source'][['start_node', 'end_node', 'value']]
    isource['isource_number']=isource.index+1
    n_isource=len(isource)

    B=np.zeros((n_nodes,n_vsource))
    D=np.zeros((n_vsource,n_vsource))
    G=np.zeros((n_nodes,n_nodes))
    for i in range(n_vnodes):
        node1 = vsource.loc[vsource['vsource_number'] == (i+1), 'start_node']
        node2 = vsource.loc[vsource['vsource_number'] == (i+1), 'end_node']
        if(not(node1==ground_node) and not(node2==ground_node)):
            if(node1[0]==node2[0]):
                if(node1[1]>node2[1]):
                    B[nodes.loc[nodes['node'] == node1, 'node_number']-1][i]=1
                    B[nodes.loc[nodes['node'] == node2, 'node_number']-1][i]=-1
                else:
                    B[nodes.loc[nodes['node'] == node1, 'node_number']-1][i]=-1
                    B[nodes.loc[nodes['node'] == node2, 'node_number']-1][i]=1
            elif(node1[1]==node2[1]):
                if(node1[0]>node2[0]):
                    B[nodes.loc[nodes['node'] == node1, 'node_number']-1][i]=-1
                    B[nodes.loc[nodes['node'] == node2, 'node_number']-1][i]=1
                else:
                    B[nodes.loc[nodes['node'] == node1, 'node_number']-1][i]=1
                    B[nodes.loc[nodes['node'] == node2, 'node_number']-1][i]=-1
        elif(node2==ground_node):
            if(node1[0]==ground_node[0]):
                if(node1[1]>ground_node[1]):
                    B[nodes.loc[nodes['node'] == node1, 'node_number']-1][i]=1
                else:
                    B[nodes.loc[nodes['node'] == node1, 'node_number']-1][i]=-1
            else:
                if(node1[0]>ground_node[0]):
                    B[nodes.loc[nodes['node'] == node1, 'node_number']-1][i]=-1
                else:
                    B[nodes.loc[nodes['node'] == node1, 'node_number']-1][i]=1
        elif(node1==ground_node):
            if(node2[0]==ground_node[0]):
                if(node2[1]>ground_node[1]):
                    B[nodes.loc[nodes['node'] == node2, 'node_number']-1][i]=1
                else:
                    B[nodes.loc[nodes['node'] == node2, 'node_number']-1][i]=-1
            else:
                if(node2[0]>ground_node[0]):
                    B[nodes.loc[nodes['node'] == node2, 'node_number']-1][i]=-1
                else:
                    B[nodes.loc[nodes['node'] == node2, 'node_number']-1][i]=1
    C=B.transpose()
    for i in range(n_nodes):
        for j in range(n_nodes):
            if(i!=j):
                n1 = nodes.loc[nodes['node_number'] == (i+1), 'node']
                n2 = nodes.loc[nodes['node_number'] == (j+1), 'node']
                g=conductance.loc[(conductance['start_node']==n1 & conductance['end_node']==n2) | (conductance['start_node']==n2 & conductance['end_node']==n1), 'value']
                G[i][j]=-g
            else:
                n1 = nodes.loc[nodes['node_number'] == (i+1), 'node']
                G[i][j]=conductance.loc[(conductance['start_node']==n1 | conductance['end_node']==n1),'value'].sum()
    A = np.bmat([[G, B], [C, D]])
    print(A)
    
if __name__ == "__main__":
    main()