# Linear_Circuit_solver

Solves linear circuits based on an improvised nodal analysis technique: visit https://lpsa.swarthmore.edu/Systems/Electrical/mna/MNA2.html for more details.
Currently supports resistances, current and voltage sources as input and solves for node voltages, branch currents. Support for inductors/capacitors/alternating circuits will be added soon.

Guidelines: 
Download 'linear_circuit_solver.py' and 'solver_gui.py' and run the latter. 

Click on a line in the grid to select and click again to deselect. Selected lines are numbered accordingly. 

Choose your ground node by entering coordinates (x,y) in the text box and click 'Set Ground'.

Once you're done with the layout, click 'Solve' and enter the type of circuit element (out of 'Resistor','Voltage Source','Current Source') that you want for each line and enter in an appropriate value for each (in SI units) and click on 'Submit'.

The final matrix obtained gives the values of the potentials at each node (except the ground node) with respect to the ground node, in numerical order, followed by the current passing through each voltage source, also in numerical order.

Note:
> Voltage sources with value set as 0 to be used as connecting wires. 
> Voltage and current sources are oriented left-right and bottom-up by default. Use negative values for right-left/up-bottom directions.
> Voltages and currents obtained in the solution matrix follow the same direction convention stated above.
