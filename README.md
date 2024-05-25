# PowerCalc
Python GUI to calculate your PSU needs
![](media/window.png?raw=true)
## setup/requirements
This setup uses 3 nonstandard python libraries and was testen on 3.10 (shouldnt be an issue)
Pillow, requests, sv_ttk
```
pip install Pillow sv_ttk requests
```
after install simply run PsuCalculator.py

## Future plans
Specify steppers by current ant voltage as thats how most people define them in klipper configs.
Add presets and components.
Possibly a non pullrequest way to submit parts? (strong maybe)

# Useage
At startup the program fetches the latest database json from this repo (if you wana add more part simply fork and pullrequest).
## Adding parts
### Custom parts
At the top you can find an input field to add your own custom parts that might not make it into the global json file

### Premade components
Below you can find the library for preconfigured parts.

### Presets
Lastly you have the preset, none excist yet but later down the line we will try to add supports for things like premade LDO kits.

### Powercalc
The powercalc simply sums up how many watts are needed for each voltage group.
NOTE! If you run a raspberry pi of a 24V mainboard. simply change the voltage cell to 24V (tough a pi will not draw that much its important to take note in general for other uses).

### Save your build
You also have the option to save your current setup to a CSV file and load it for later use or sharing with others.

### Component list
At the top you will find a remove button, to use simply click any entry anc confirm by clicking the button.

Every field is editable, though voltage is locked to 5,12,24,48,120,230 volts.

| Header  | comment |
| ------------- | ------------- |
| Type  | which category the component was pulled from |
| Component  | basic partname   |
| Power Draw (W) | How much wattage your parts draws at max |
| Voltage (V) | Operating voltage |
| %   | Load percentage that caps you part (like how beds are often at 80% in klipper config |
| Amount | Lets you specify multiple of the same part |
| Specific link | Link field for hidden gems like cheap ali hotends ect |




