import json
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import webbrowser
import os
import sv_ttk
import requests
from tkinter import filedialog
import csv

class PowerCalculatorGUI(tk.Tk):
    def __init__(self, config_file):
        super().__init__()
        self.title("Toolchanger power calculator")
        self.geometry("1200x1200")
        self.config_data = config_file
        self.components = []
        self.preconfigured_components = {}
        self.load_preconfigured_components(config_file)

        self.create_widgets()

    def load_preconfigured_components(self, config_file):
        try:
            data = config_file
            self.preconfigured_components = data['components']
            self.component_types = list(self.preconfigured_components.keys())
        except FileNotFoundError:
            messagebox.showerror("File Not Found", f"Configuration file '{config_file}' not found.")
            self.preconfigured_components = {}
            self.component_types = []

    def create_widgets(self):
        left_frame = ttk.Frame(self)
        left_frame.pack(side="left", fill="y", padx=5, pady=10)


        # ------------------------- custom components ------------------------- 
        self.add_custom_frame = ttk.LabelFrame(left_frame, text="Add Custom Component")
        self.add_custom_frame.pack(fill="x", padx=10, pady=5)

        self.custom_type_label = ttk.Label(self.add_custom_frame, text="Type:", font=("Helvetica", 14, "bold"))
        self.custom_type_label.grid(row=0, column=0, padx=5, pady=5)
        self.custom_type_entry = ttk.Entry(self.add_custom_frame)
        self.custom_type_entry.grid(row=0, column=1, padx=5, pady=5)

        self.custom_name_label = ttk.Label(self.add_custom_frame, text="Name:", font=("Helvetica", 14, "bold"))
        self.custom_name_label.grid(row=1, column=0, padx=5, pady=5)
        self.custom_name_entry = ttk.Entry(self.add_custom_frame)
        self.custom_name_entry.grid(row=1, column=1, padx=5, pady=5)

        self.custom_power_label = ttk.Label(self.add_custom_frame, text="Power Draw (W):", font=("Helvetica", 14, "bold"))
        self.custom_power_label.grid(row=2, column=0, padx=5, pady=5)
        self.custom_power_entry = ttk.Entry(self.add_custom_frame)
        self.custom_power_entry.grid(row=2, column=1, padx=5, pady=5)

        self.custom_Voltage_entry = ttk.Label(self.add_custom_frame, text="Voltage (V):", font=("Helvetica", 14, "bold"))
        self.custom_Voltage_entry.grid(row=3, column=0, padx=5, pady=5)
        self.custom_Voltage_entry = ttk.Entry(self.add_custom_frame)
        self.custom_Voltage_entry.grid(row=3, column=1, padx=5, pady=5)

        self.add_custom_button = ttk.Button(self.add_custom_frame, text="Add Custom Component", command=self.add_custom_component)
        self.add_custom_button.grid(row=4, column=0, columnspan=2, pady=10)


        # ------------------------- preconfigured components ------------------------- 
        self.add_preconfigured_frame = ttk.LabelFrame(left_frame, text="Add Preconfigured Component")
        self.add_preconfigured_frame.pack(fill="x", padx=10, pady=5)

        self.component_type_label = ttk.Label(self.add_preconfigured_frame, text="Component Type:", font=("Helvetica", 14, "bold"))
        self.component_type_label.grid(row=0, column=0, padx=5, pady=5)

        self.component_type_combo = ttk.Combobox(self.add_preconfigured_frame, values=self.component_types)
        self.component_type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.component_type_combo.bind("<<ComboboxSelected>>", self.update_component_combo)

        self.preconfigured_component_label = ttk.Label(self.add_preconfigured_frame, text="Component:", font=("Helvetica", 14, "bold"))
        self.preconfigured_component_label.grid(row=1, column=0, padx=5, pady=5)

        self.preconfigured_component_combo = ttk.Combobox(self.add_preconfigured_frame)
        self.preconfigured_component_combo.grid(row=1, column=1, padx=5, pady=5)

        self.add_preconfigured_button = ttk.Button(self.add_preconfigured_frame, text="Add Preconfigured Component", command=self.add_preconfigured_component)
        self.add_preconfigured_button.grid(row=2, column=0, columnspan=2, pady=10)


        # ------------------------- Preset selection ------------------------- 
        self.add_Loadout_frame = ttk.LabelFrame(left_frame, text="Add Loadout")
        self.add_Loadout_frame.pack(fill="x", padx=10, pady=5)

        self.Loadout_label = ttk.Label(self.add_Loadout_frame, text="Select preset:", font=("Helvetica", 14, "bold"))
        self.Loadout_label.grid(row=0, column=0, padx=5, pady=5)

        self.Loadout_combo = ttk.Combobox(self.add_Loadout_frame, values=list(self.config_data["presets"].keys()))
        self.Loadout_combo.grid(row=0, column=1, padx=5, pady=5)

        self.add_Loadout_button = ttk.Button(self.add_Loadout_frame, text="Add Preset Components", command=self.add_preset_components)
        self.add_Loadout_button.grid(row=2, column=0, columnspan=2, pady=10)


        # ------------------------- components list tree ------------------------- 
        self.component_list_frame = ttk.LabelFrame(self, text="Components")
        self.component_list_frame.pack(side="left", fill="both", expand=True, padx=5, pady=10)

        self.remove_button = ttk.Button(self.component_list_frame, text="Remove Selected Component", command=self.remove_selected_component)
        self.remove_button.pack(fill="x", padx=10, pady=5)

        self.tree_frame = ttk.Frame(self.component_list_frame)
        self.tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(self.tree_frame, columns=("Type", "Name", "Power Draw", "Voltage", "Percentage", "Amount", "Specific link"), show="headings")
        self.tree.pack(fill="both", expand=True)

        self.tree.heading("Type"            , text="Type")
        self.tree.heading("Name"            , text="Component")
        self.tree.heading("Power Draw"      , text="Power Draw (W)")
        self.tree.heading("Voltage"         , text="Voltage (V)")
        self.tree.heading("Percentage"      , text="%")
        self.tree.heading("Amount"          , text="Amount")
        self.tree.heading("Specific link"   , text="Specific link")

        self.tree.column("Type"         , anchor="w"     , width=100)
        self.tree.column("Name"         , anchor="w"     , width=200)
        self.tree.column("Power Draw"   , anchor="center", width=100)
        self.tree.column("Voltage"      , anchor="center", width=100)
        self.tree.column("Percentage"   , anchor="center", width=50 )
        self.tree.column("Amount"       , anchor="center", width=50 )
        self.tree.column("Specific link", anchor="center", width=200)

        self.tree.bind("<Double-1>", self.on_double_click)

        # ------------------------- Power calculation ------------------------- 
        total_frame = ttk.Frame(left_frame)
        total_frame.pack(fill="x", pady=10)

        bottom_frame = ttk.Frame(left_frame)
        bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.total_power_label = ttk.Label(left_frame, text="Total Power Draw", font=("Helvetica", 16, "bold"))
        self.total_power_label.pack(side="top",fill = "x", padx = 10, pady=10)

        self.total_power_label_230V = ttk.Label(left_frame, text="230V : 0W", font=("Helvetica", 12, "bold"))
        self.total_power_label_230V.pack(side="top",fill = "x", padx = 10, pady=10)

        self.total_power_label_120V = ttk.Label(left_frame, text="120V : 0W", font=("Helvetica", 12, "bold"))
        self.total_power_label_120V.pack(side="top",fill = "x", padx = 10, pady=10)        

        self.total_power_label_48V = ttk.Label(left_frame, text="48V : 0W", font=("Helvetica", 12, "bold"))
        self.total_power_label_48V.pack(side="top",fill = "x", padx = 10, pady=10)

        self.total_power_label_24V = ttk.Label(left_frame, text="24V : 0W", font=("Helvetica", 12, "bold"))
        self.total_power_label_24V.pack(side="top",fill = "x", padx = 10, pady=10)

        self.total_power_label_12V = ttk.Label(left_frame, text="12V : 0W", font=("Helvetica", 12, "bold"))
        self.total_power_label_12V.pack(side="top",fill = "x", padx = 10, pady=10)

        self.total_power_label_5V = ttk.Label(left_frame, text="5V : 0W", font=("Helvetica", 12, "bold"))
        self.total_power_label_5V.pack(side="top",fill = "x", padx = 10, pady=10)

        # ------------------------- save config ---------------------------
        self.add_file_frame = ttk.LabelFrame(left_frame, text="Add Preconfigured Component")
        self.add_file_frame.pack(fill="x", padx=10, pady=5)

        self.add_file_save_button = ttk.Button(self.add_file_frame, text="Save this build", command=self.save_current_treeview)
        self.add_file_save_button.grid(row=0, column=0, columnspan=1, padx = 10, pady=10)

        self.add_file_load_button = ttk.Button(self.add_file_frame, text="Load previous build", command=self.load_treeview_data)
        self.add_file_load_button.grid(row=0, column=1, columnspan=1, padx = 10, pady=10)


        # ------------------------- Logo ------------------------- 
        image=Image.open(requests.get("https://raw.githubusercontent.com/DraftShift/PowerCalc/main/media/PowerCalc_logo.png?raw=true", stream=True).raw)
        resized = image.resize((200,200))
        logo = ImageTk.PhotoImage(resized)

        self.logo_label = ttk.Label(bottom_frame, image=logo)
        self.logo_label.image = logo
        self.logo_label.pack(side="left", pady=5)
        self.logo_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/DraftShift/PowerCalc"))  # Replace with your GitHub link

    def update_component_combo(self, event):
        component_type = self.component_type_combo.get()
        if component_type in self.preconfigured_components:
            components = self.preconfigured_components[component_type]
            self.preconfigured_component_combo['values'] = [comp['name'] for comp in components]
        else:
            self.preconfigured_component_combo['values'] = []

    def update_total_power_draw(self):
        power_by_voltage = {230: 0, 120: 0, 48: 0, 24: 0, 12: 0, 5: 0}

        # Iterate through all items in the treeview
        for item_id in self.tree.get_children():
            item = self.tree.item(item_id)
            values = item['values']

            voltage = int(values[3])  # Assuming 'Voltage' is the 4th column
            power_draw = float(values[2])  # Assuming 'Power Draw' is the 3rd column
            percentage = float(values[4])  # Assuming 'Percentage' is the 5th column
            amount = int(values[5])  # Assuming 'Amount' is the 6th column

            calculated_power = power_draw * (percentage / 100) * amount
            if voltage in power_by_voltage:
                power_by_voltage[voltage] += calculated_power

        self.total_power_label_230V.config(text=f"230V: {power_by_voltage[230]:.2f}W")
        self.total_power_label_120V.config(text=f"120V: {power_by_voltage[120]:.2f}W")
        self.total_power_label_48V.config(text=f"48V: {power_by_voltage[48]:.2f}W")
        self.total_power_label_24V.config(text=f"24V: {power_by_voltage[24]:.2f}W")
        self.total_power_label_12V.config(text=f"12V: {power_by_voltage[12]:.2f}W")
        self.total_power_label_5V.config(text=f"5V: {power_by_voltage[5]:.2f}W")

    def add_custom_component(self):
        name = self.custom_name_entry.get()
        Type = self.custom_type_entry.get()
        power_draw = float(self.custom_power_entry.get())
        Voltage = self.custom_Voltage_entry.get()
        #percentage = float(self.custom_percentage_entry.get())
        #amount = int(self.custom_amount_entry.get())
        component_id = self.tree.insert("", "end", values=(Type, name, power_draw,Voltage, 100,1))#percentage, amount
        component = {"id": component_id,"Type": Type, "name": name, "power_draw": power_draw, "Voltage": Voltage, "percentage": 100, "amount": 1, "Specific link": "NaN"}
        self.components.append(component)
        self.update_total_power_draw()

    def add_preconfigured_component(self):
        component_type = self.component_type_combo.get()
        component_name = self.preconfigured_component_combo.get()
        
        if component_type in self.preconfigured_components:
            component = next((comp for comp in self.preconfigured_components[component_type] if comp["name"] == component_name), None)
            component_id = self.tree.insert("", "end", values=(component_type,component_name, component["power_draw"], component["Voltage"],100, 1))
            if component:
                self.components.append({"id": component_id, "Type": component_type,"name": component_name, "power_draw": component["power_draw"], "Voltage": component["Voltage"], "percentage": 100, "amount": 1, "Specific link": component["link"]})
                #self.update_component_list()
                self.update_total_power_draw()
            else:
                messagebox.showerror("Component not found", f"Component '{component_name}' not found in selected type.")
        else:
            messagebox.showerror("Invalid type", f"Component type '{component_type}' is not valid.")

    def remove_selected_component(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item[0])
            self.components = [comp for comp in self.components if comp['id'] != selected_item[0]]
            self.update_total_power_draw()
        else:
            messagebox.showerror("Selection Error", "Please select an item to remove.")

    def populate_presets(self):
        presets = list(self.config_data.get("presets", {}).keys())
        self.Loadout_combo['values'] = presets

    def add_preset_components(self):
        selected_preset = self.Loadout_combo.get()
        print(f"Selected Preset: {selected_preset}")  # Debugging statement
        component_names = self.config_data["presets"].get(selected_preset, [])
        print(component_names)
        # Insert components from the preset
        for component_name in component_names:
            component = self.find_component(component_name)
            component_type = self.find_component_type(component_name)
            print(component)
            if component:
                component_id = len(self.components) + 1  # or use a different method to generate unique IDs
                self.components.append({
                    "id": component_id,
                    "Type": component_type,
                    "name": component_name,
                    "power_draw": component["power_draw"],
                    "Voltage": component["Voltage"],
                    "percentage": 100,
                    "amount": 1,
                    "Specific link": component["link"]
                })
                self.tree.insert("", "end", values=(
                    component_type, component["name"], component["power_draw"], component["Voltage"], 100, 1, component["link"]))
        self.update_total_power_draw()

    def find_component(self, component_name):
        for category, components in self.preconfigured_components.items():
            for component in components:
                if component["name"] == component_name:
                    return component
        return None

    def find_component_type(self, component_name):
        for category, components in self.preconfigured_components.items():
            for component in components:
                if component["name"] == component_name:
                    return category
        return "Unknown"

    def on_double_click(self, event):
        # Identify the region and the column clicked
        region_clicked = self.tree.identify_region(event.x, event.y)
        if region_clicked not in ("cell"):
            return

        column = self.tree.identify_column(event.x)
        selected_iid = self.tree.focus()
        selected_values = self.tree.item(selected_iid)['values']

        # Determine the column index
        col = int(column[1:]) - 1  # subtract 1 because columns are 1-indexed

        # Get the x, y coordinates of the clicked cell
        x, y, width, height = self.tree.bbox(selected_iid, column)

        # If the column is "Voltage", use a Combobox with predefined values
        if col == 3:  # Assuming 'Voltage' is the 4th column (index 3)
            self.entry = ttk.Combobox(self.tree, values=[230, 120, 48, 24, 12, 5])
            self.entry.place(x=x, y=y, width=width, height=height)
            self.entry.set(selected_values[col])
        else:
            # Create an Entry widget for editing other cells
            self.entry = ttk.Entry(self.tree)
            self.entry.place(x=x, y=y, width=width, height=height)
            self.entry.insert(0, selected_values[col])
            self.entry.selection_range(0, tk.END)  # Highlight the contents

        self.entry.focus()

        # Bind the widget to an event that will save the new value
        self.entry.bind('<Return>', lambda e: self.update_cell_value(selected_iid, col))
        self.entry.bind('<FocusOut>', lambda e: self.update_cell_value(selected_iid, col))

    def update_cell_value(self, iid, col):
        new_value = self.entry.get()
        current_values = self.tree.item(iid)['values']
        current_values[col] = new_value

        self.tree.item(iid, values=current_values)
        self.entry.destroy()
        self.update_total_power_draw()

    def save_treeview_to_csv(self):
        initial_file = "treeview_data.csv"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=initial_file  # Provide a default filename
        )
        if not file_path:
            return  # User cancelled the save dialog

        # Check if the file already exists and append a number if it does
        if os.path.exists(file_path):
            base, extension = os.path.splitext(file_path)
            counter = 1
            new_file_path = f"{base}_{counter}{extension}"
            while os.path.exists(new_file_path):
                counter += 1
                new_file_path = f"{base}_{counter}{extension}"
            file_path = new_file_path

        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write the header
            writer.writerow(["Type", "Name", "Power Draw", "Voltage", "Percentage", "Amount", "Specific link"])

            # Write the data
            for item_id in self.tree.get_children():
                row = self.tree.item(item_id)['values']
                writer.writerow(row)

    def load_treeview_from_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return  # User cancelled the open dialog

        with open(file_path, mode='r') as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip the header row
            for row in reader:
                self.tree.insert("", "end", values=row)
            self.update_total_power_draw()

    def save_current_treeview(self):
        self.save_treeview_to_csv()

    def load_treeview_data(self):
        self.load_treeview_from_csv()

if __name__ == "__main__":
    url = 'https://raw.githubusercontent.com/DraftShift/PowerCalc/main/3d_printer_components.json'
    resp = requests.get(url)
    data = json.loads(resp.text)
    app = PowerCalculatorGUI(data)
    sv_ttk.use_dark_theme()
    app.mainloop()
