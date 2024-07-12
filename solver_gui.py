import tkinter as tk
from tkinter import ttk


class GridGUI:
    
    def __init__(self, master, size=5, cell_size=50):
        self.master = master
        self.size = size
        self.cell_size = cell_size
        self.canvas_size = cell_size * size

        self.frame = tk.Frame(master)
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.grid_frame = tk.Frame(self.frame)
        self.grid_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.canvas = tk.Canvas(self.grid_frame, width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()

        self.control_frame = tk.Frame(self.frame)
        self.control_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        self.lines = {}
        self.selected_lines = []
        self.component_vars = {}
        self.draw_grid()
        self.canvas.bind("<Button-1>", self.on_click)

        self.create_controls()

        self.center_frame()

        self.gnd = None

    def center_frame(self):
        self.master.update()
        window_width = self.master.winfo_width()
        window_height = self.master.winfo_height()
        frame_width = self.frame.winfo_width()
        frame_height = self.frame.winfo_height()
        x = (window_width - frame_width) // 2
        y = (window_height - frame_height) // 2
        self.frame.place(x=x, y=y)

    def draw_grid(self):
        for i in range(self.size + 1):
            x = i * self.cell_size
            for j in range(self.size):
                y = j * self.cell_size
                line_id = self.canvas.create_line(x, y, x, y + self.cell_size, fill="black")
                self.lines[(j, i, j+1, i)] = line_id

        for i in range(self.size):
            y = i * self.cell_size
            for j in range(self.size + 1):
                x = j * self.cell_size
                line_id = self.canvas.create_line(x, y, x + self.cell_size, y, fill="black")
                self.lines[(i, j, i, j+1)] = line_id

        for i in range(self.size + 1):
            for j in range(self.size + 1):
                y, x = i * self.cell_size, j * self.cell_size
                self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="black")

    def create_controls(self):
        self.confirm_button = tk.Button(self.control_frame, text="Confirm", command=self.confirm_components)
        self.confirm_button.pack(pady=10)

    def confirm_components(self):
        confirm_window = tk.Toplevel(self.master)
        confirm_window.title("Confirm Components")

        for index, line_key in enumerate(self.selected_lines, start=1):
            frame = tk.Frame(confirm_window)
            frame.pack(pady=5, fill=tk.X)

            tk.Label(frame, text=f"Index {index}:").pack(side=tk.LEFT)

            type_var = tk.StringVar()
            type_menu = ttk.Combobox(frame, textvariable=type_var, values=("Voltage Source", "Current Source", "Resistor", "Capacitor", "Inductor"))
            type_menu.pack(side=tk.LEFT, padx=5)

            value_var = tk.StringVar()
            value_entry = tk.Entry(frame, textvariable=value_var)
            value_entry.pack(side=tk.LEFT, padx=5)

            self.component_vars[line_key] = {'type': type_var, 'value': value_var}

        tk.Button(confirm_window, text="Save", command=lambda: self.save_components(confirm_window)).pack(pady=10)

    def save_components(self, window):
        for line_key, vars in self.component_vars.items():
            component_type = vars['type'].get()
            component_value = vars['value'].get()
            if component_type and component_value:  # Only save if both fields are filled
                self.component_vars[line_key] = {'type': component_type, 'value': component_value}
            else:
                self.component_vars.pop(line_key, None)  # Remove if fields are empty
        print("Components saved:", self.component_vars)
        window.destroy()
        self.enable_node_selection()
        
        
    def enable_node_selection(self):
        self.canvas.bind("<Button-1>", self.on_node_click)

    def on_node_click(self, event):
        if self.gnd is not None:
            return  # Do nothing if ground node is already set
        x, y = event.x, event.y
        node_row, node_col = y // self.cell_size, x // self.cell_size
        if (x % self.cell_size < 5) and (y % self.cell_size < 5):
            self.gnd = (node_col, node_row)
            self.display_ground_node()
            self.canvas.unbind("<Button-1>")

    def display_ground_node(self):
        if self.gnd is not None:
            ground_label = tk.Label(self.control_frame, text=f"Ground node: {self.gnd}")
            ground_label.pack(pady=10)

    def on_click(self, event):
        x, y = event.x, event.y
        cell_row, cell_col = y // self.cell_size, x // self.cell_size

        if x % self.cell_size < 5:
            if 0 <= cell_row < self.size and 0 <= cell_col < self.size:
                line_key = (cell_col, cell_row, cell_col+1, cell_row)
        elif y % self.cell_size < 5:
            if 0 <= cell_row < self.size and 0 <= cell_col < self.size:
                line_key = (cell_col, cell_row, cell_col, cell_row+1)
        else:
            return

        if line_key in self.lines:
            line_id = self.lines[line_key]
            current_color = self.canvas.itemcget(line_id, "fill")
            if current_color == "black":
                new_color = "red"
                self.selected_lines.append(line_key)
                index = len(self.selected_lines)
                self.canvas.itemconfig(line_id, fill=new_color)
                self.canvas.create_text(
                    (line_key[1] + line_key[3]) * self.cell_size / 2,
                    (line_key[0] + line_key[2]) * self.cell_size / 2,
                    text=str(index),
                    fill="white"
                )
            else:
                new_color = "black"
                if line_key in self.selected_lines:
                    self.selected_lines.remove(line_key)
                self.canvas.itemconfig(line_id, fill=new_color)
                for item in self.canvas.find_overlapping(
                    (line_key[1] + line_key[3]) * self.cell_size / 2 - 1,
                    (line_key[0] + line_key[2]) * self.cell_size / 2 - 1,
                    (line_key[1] + line_key[3]) * self.cell_size / 2 + 1,
                    (line_key[0] + line_key[2]) * self.cell_size / 2 + 1
                ):
                    if self.canvas.type(item) == "text":
                        self.canvas.delete(item)

            self.update_indices()
    
        
    def update_indices(self):
        for item in self.canvas.find_all():
            if self.canvas.type(item) == "text":
                self.canvas.delete(item)

        for index, line_key in enumerate(self.selected_lines, start=1):
            self.canvas.create_text(
                (line_key[1] + line_key[3]) * self.cell_size / 2,
                (line_key[0] + line_key[2]) * self.cell_size / 2,
                text=str(index),
                fill="white"
            )

