import tkinter as tk
from tkinter import messagebox,ttk
from linear_circuit_solver import handle_submit
import pandas as pd
import numpy as np

class GridGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("GUI")
        
        window_size = 800
        self.master.geometry(f"{window_size}x{window_size}")
        
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(side=tk.TOP, pady=10)
        
        self.solve_button = tk.Button(self.button_frame, text="Solve", command=self.solve,
                                      font=("Arial", 14), padx=20, pady=10)
        self.solve_button.pack(side=tk.LEFT, padx=10)

       
        self.input_frame = tk.Frame(self.master)
        self.input_frame.pack(side=tk.TOP, pady=10)

        self.ground_node_label = tk.Label(self.input_frame, text="Enter ground node (x,y):", font=("Arial", 12))
        self.ground_node_label.pack(side=tk.LEFT, padx=5)

        self.ground_node_entry = tk.Entry(self.input_frame, font=("Arial", 12), width=10)
        self.ground_node_entry.pack(side=tk.LEFT, padx=5)

        self.ground_node_button = tk.Button(self.input_frame, text="Set Ground", command=self.set_ground_node,
                                            font=("Arial", 12), padx=10, pady=5)
        self.ground_node_button.pack(side=tk.LEFT, padx=5)
        
        self.canvas = tk.Canvas(self.master, width=window_size, height=window_size-150)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.line_count = 0
        self.line_data = {}
        self.element_input_window = None
        self.active_line_coords = []
        self.active_lines = []
        self.ground_node = None
        
        self.draw_grid()
        
        self.master.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Button-1>", self.on_click)

    def set_ground_node(self):
        input_str = self.ground_node_entry.get()
        x, y = map(int, input_str.strip('()').split(','))  
        self.ground_node = (x, y)
        self.highlight_ground_node()
            

    def highlight_ground_node(self):
        self.canvas.delete("ground_highlight")
        if self.ground_node:
            x, y = self.ground_node
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            grid_size = min(width, height) * 0.8
            offset_x = (width - grid_size) / 2
            offset_y = (height - grid_size) / 2
            cell_size = grid_size / 14
            
            node_x = offset_x + x * cell_size
            node_y = offset_y + y * cell_size
            
            self.canvas.create_oval(node_x - 5, node_y - 5, node_x + 5, node_y + 5,
                                    fill="yellow", outline="red", width=2, tags="ground_highlight")

    def draw_grid(self):
        self.canvas.delete("all")
        self.line_data.clear()
    
        
        active_coords = [(line['coords'], line['number']) for line in self.active_lines]
        self.active_lines.clear()
    
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
    
        grid_size = min(width, height) * 0.8
        offset_x = (width - grid_size) / 2
        offset_y = (height - grid_size) / 2
        cell_size = grid_size / 14

        node_radius = min(cell_size / 10, 5)
        click_width = max(cell_size / 5, 10)  # Width of clickable area
    
        
        for i in range(15):
            x = offset_x + i * cell_size
            self.canvas.create_line(x, offset_y, x, offset_y + grid_size, tags="grid")
            self.canvas.create_text(x, offset_y - 10, text=str(i), anchor="s", tags="grid_number")
        
            
            y = offset_y + i * cell_size
            self.canvas.create_line(offset_x, y, offset_x + grid_size, y, tags="grid")
            self.canvas.create_text(offset_x - 10, y, text=str(i), anchor="e", tags="grid_number")
        
            for j in range(15):
                y = offset_y + j * cell_size
                self.canvas.create_oval(x - node_radius, y - node_radius, 
                                    x + node_radius, y + node_radius, 
                                    fill="black", tags="node")
            
                if i < 14:
                    line_id = self.canvas.create_line(x, y, x + cell_size, y, width=2, tags="line")
                    rect_id = self.canvas.create_rectangle(x, y - click_width/2, x + cell_size, y + click_width/2, 
                                                      fill="", outline="", tags="clickable")
                    self.line_data[line_id] = {"coords": (i, j, i+1, j), "clicked": False, "number": None}
            
                if j < 14:
                    line_id = self.canvas.create_line(x, y, x, y + cell_size, width=2, tags="line")
                    rect_id = self.canvas.create_rectangle(x - click_width/2, y, x + click_width/2, y + cell_size, 
                                                      fill="", outline="", tags="clickable")
                    self.line_data[line_id] = {"coords": (i, j, i, j+1), "clicked": False, "number": None}
    
        
        for coords, number in active_coords:
            self.activate_line_by_coords(coords, number)
    
       
        self.highlight_ground_node()

    def get_line_grid_coords(self, rect_id):
        line_id = self.line_data[rect_id]['line_id']
        coords = self.canvas.coords(line_id)
        return self.pixel_to_grid_coords(coords)

    def activate_line_by_coords(self, coords, number):
        for line_id, data in self.line_data.items():
            if data['coords'] == coords:
                self.activate_line(line_id, number)
                break

    def activate_line(self, line_id, number=None):
        if number is None:
            self.line_count += 1
            number = self.line_count
        self.canvas.itemconfig(line_id, fill="red", width=3)
        self.line_data[line_id]['clicked'] = True
        self.line_data[line_id]['number'] = number
        self.active_lines.append(self.line_data[line_id])
        self.update_line_number(line_id)
            
    def deactivate_line(self, line_id):
        self.canvas.itemconfig(line_id, fill="black", width=2)
        self.line_data[line_id]["clicked"] = False
        self.active_lines = [line for line in self.active_lines if line["coords"] != self.line_data[line_id]["coords"]]
        self.canvas.delete(f"number_{line_id}")
        self.renumber_lines()

    def renumber_lines(self):
        self.line_count = 0
        for line in self.active_lines:
            self.line_count += 1
            line["number"] = self.line_count
            for line_id, data in self.line_data.items():
                if data["coords"] == line["coords"]:
                    self.update_line_number(line_id)
                    break

    def on_click(self, event):
        clicked_items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item in clicked_items:
            if "line" in self.canvas.gettags(item):
                if not self.line_data[item]["clicked"]:
                    self.activate_line(item)
                else:
                    self.deactivate_line(item)
                break

    def update_line_number(self, line_id):
        self.canvas.delete(f"number_{line_id}")
        coords = self.canvas.coords(line_id)
        mid_x = (coords[0] + coords[2]) / 2
        mid_y = (coords[1] + coords[3]) / 2
        self.canvas.create_text(mid_x, mid_y, text=str(self.line_data[line_id]['number']),
                                    fill="blue", font=("Arial", 10, "bold"),
                                    tags=f"number_{line_id}")

    def solve(self):                        
        if self.element_input_window is None or not self.element_input_window.winfo_exists():
            self.element_input_window = tk.Toplevel(self.master)
            ElementInputWindow(self.element_input_window, self.active_lines, self.ground_node, self.handle_submit)
        else:
            self.element_input_window.lift()

    def handle_submit(self, circuit_data):        
        handle_submit(circuit_data)
        
    def on_resize(self, event):        
        self.draw_grid()
            
    def pixel_to_grid_coords(self, pixel_coords):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        grid_size = min(width, height) * 0.8
        offset_x = (width - grid_size) / 2
        offset_y = (height - grid_size) / 2
        cell_size = grid_size / 14

        grid_coords = []
        for i in range(0, len(pixel_coords), 2):
            x = round((pixel_coords[i] - offset_x) / cell_size)
            y = round((pixel_coords[i+1] - offset_y) / cell_size)
            grid_coords.extend([x, y])

        return grid_coords    
        
class ElementInputWindow:
    def __init__(self, master, active_lines, ground_node, submit_callback):
        self.master = master
        self.master.title("Element Input")
        self.active_lines = active_lines
        self.ground_node = ground_node
        self.submit_callback = submit_callback
        self.element_inputs = []
        
        self.create_widgets()

    def create_widgets(self):
        for line in self.active_lines:
            frame = ttk.Frame(self.master)
            frame.pack(pady=5, padx=10, fill='x')
            
            coord_str = f"({line['coords'][0]},{line['coords'][1]}) to ({line['coords'][2]},{line['coords'][3]})"
            ttk.Label(frame, text=f"Line {line['number']} {coord_str}:").pack(side='left')
            
            element_type = ttk.Combobox(frame, values=['resistor', 'voltage source', 'current source'])
            element_type.pack(side='left', padx=5)
            element_type.set('resistor')  # default value
            
            value_entry = ttk.Entry(frame)
            value_entry.pack(side='left', padx=5)
            
            self.element_inputs.append((element_type, value_entry))
        
        submit_button = ttk.Button(self.master, text="Submit", command=self.submit)
        submit_button.pack(pady=10)

    def submit(self):
        
        circuit_data = {
            'ground_node': self.ground_node,
            'elements': []
        }
        
        for line, (element_type, value_entry) in zip(self.active_lines, self.element_inputs):
            element_data = {
                'number': line['number'],
                'type': element_type.get(),
                'value': value_entry.get(),
                'coordinates': line['coords']
            }
            circuit_data['elements'].append(element_data)
        
        self.submit_callback(circuit_data)
        self.master.withdraw()  
        
    
if __name__ == "__main__":
    root = tk.Tk()
    app = GridGUI(root)
    root.mainloop()

