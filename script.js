const components = [];
let preconfiguredComponents = {};
let premadeBuilds = {};

const preconfiguredComponentsUrl = 'https://raw.githubusercontent.com/DraftShift/PowerCalc/main/3d_printer_components.json';
const premadeBuildsUrl = 'premade_printer_builds.json';

fetch(preconfiguredComponentsUrl)
    .then(response => response.json())
    .then(data => {
        preconfiguredComponents = data.components;
        console.log('Preconfigured components:', preconfiguredComponents);
        populatePresetTypes();
    })
    .catch(error => console.error('Error loading preconfigured components:', error));

fetch(premadeBuildsUrl)
    .then(response => response.json())
    .then(data => {
        premadeBuilds = data.builds;
        populatePremadeBuilds();
    })
    .catch(error => console.error('Error loading premade builds:', error));

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('custom-component-form').addEventListener('submit', addCustomComponent);
    document.getElementById('add-preset-button').addEventListener('click', addPresetComponent);
    document.getElementById('add-build-button').addEventListener('click', addPremadeBuild);
    document.getElementById('save-button').addEventListener('click', saveCurrentBuild);
    document.getElementById('load-button').addEventListener('click', loadPreviousBuild);

    document.getElementById('preset-type').addEventListener('change', populatePresetNames);
    renderTable();
});

function addCustomComponent(event) {
    event.preventDefault();
    const type = document.getElementById('custom-type').value;
    const name = document.getElementById('custom-name').value;
    const powerDraw = parseFloat(document.getElementById('custom-power').value);
    const voltage = parseFloat(document.getElementById('custom-voltage').value);

    if (isNaN(powerDraw) || isNaN(voltage)) {
        alert("Power Draw and Voltage must be numeric values.");
        return;
    }

    const component = {
        type,
        name,
        powerDraw,
        voltage,
        percentage: 100,
        amount: 1,
        specificLink: 'NaN'
    };

    components.push(component);
    renderTable();
    updateTotalPowerDraw();
}

function addPresetComponent() {
    const type = document.getElementById('preset-type').value;
    const name = document.getElementById('preset-name').value;

    const component = preconfiguredComponents[type].find(comp => comp.name === name);
    if (component) {
        const newComponent = {
            type,
            name: component.name,
            powerDraw: parseFloat(component.powerDraw), // Correct field name
            voltage: parseFloat(component.voltage), // Correct field name
            percentage: 100,
            amount: 1,
            specificLink: component.link || 'NaN'
        };
        components.push(newComponent);
        renderTable();
        updateTotalPowerDraw();
    }
}

function addPremadeBuild() {
    const buildName = document.getElementById('premade-build').value;
    const build = premadeBuilds[buildName];

    if (build) {
        build.components.forEach(comp => {
            const component = preconfiguredComponents[comp.type].find(c => c.name === comp.name);
            if (component) {
                const newComponent = {
                    type: comp.type,
                    name: component.name,
                    powerDraw: parseFloat(component.powerDraw), // Correct field name
                    voltage: parseFloat(component.voltage), // Correct field name
                    percentage: 100,
                    amount: comp.amount,
                    specificLink: component.link || 'NaN'
                };
                components.push(newComponent);
            }
        });
        renderTable();
        updateTotalPowerDraw();
    }
}

function populatePresetTypes() {
    const presetTypeSelect = document.getElementById('preset-type');
    presetTypeSelect.innerHTML = '<option value="">Select a type</option>';

    Object.keys(preconfiguredComponents).forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        presetTypeSelect.appendChild(option);
    });
}

function populatePresetNames() {
    const type = document.getElementById('preset-type').value;
    const presetNameSelect = document.getElementById('preset-name');
    presetNameSelect.innerHTML = '<option value="">Select a name</option>';

    if (type) {
        preconfiguredComponents[type].forEach(component => {
            const option = document.createElement('option');
            option.value = component.name;
            option.textContent = component.name;
            presetNameSelect.appendChild(option);
        });
    }
}

function populatePremadeBuilds() {
    const premadeBuildSelect = document.getElementById('premade-build');
    premadeBuildSelect.innerHTML = '<option value="">Select a build</option>';

    Object.keys(premadeBuilds).forEach(build => {
        const option = document.createElement('option');
        option.value = build;
        option.textContent = build;
        premadeBuildSelect.appendChild(option);
    });
}

function renderTable() {
    const voltageOptions = `
        <option value="230">230V</option>
        <option value="120">120V</option>
        <option value="48">48V</option>
        <option value="24">24V</option>
        <option value="12">12V</option>
        <option value="5">5V</option>
    `;
    const tableBody = document.getElementById('components-table');
    tableBody.innerHTML = '';
    components.forEach((component, index) => {
        console.log('Rendering component:', component);
        const row = document.createElement('tr');
        row.innerHTML = `
            <td contenteditable="true" onblur="updateComponent(${index}, 'type', this.innerText)" class="col-type">${component.type}</td>
            <td contenteditable="true" onblur="updateComponent(${index}, 'name', this.innerText)" class="col-name">${component.name}</td>
            <td contenteditable="true" onblur="updateComponent(${index}, 'powerDraw', this.innerText)" class="col-power">${component.powerDraw}</td>
            <td class="col-voltage">
                <select onchange="updateComponent(${index}, 'voltage', this.value)" class="form-control bg-light-dark text-white">
                    ${voltageOptions}
                </select>
            </td>
            <td contenteditable="true" onblur="updateComponent(${index}, 'percentage', this.innerText)" class="col-percentage">${component.percentage}</td>
            <td contenteditable="true" onblur="updateComponent(${index}, 'amount', this.innerText)" class="col-amount">${component.amount}</td>
            <td contenteditable="true" onblur="updateComponent(${index}, 'specificLink', this.innerText)" class="col-link">${component.specificLink}</td>
            <td class="col-action"><button class="btn btn-danger" onclick="removeComponent(${index})">Remove</button></td>
        `;
        // Set the selected voltage
        console.log(`Setting voltage for component ${component.name}: ${component.voltage}`);
        row.querySelector('select').value = component.voltage;
        tableBody.appendChild(row);
    });
}

function updateComponent(index, field, value) {
    if (['powerDraw', 'voltage', 'percentage', 'amount'].includes(field)) {
        value = parseFloat(value);
        if (isNaN(value)) {
            alert(`${field.charAt(0).toUpperCase() + field.slice(1)} must be a numeric value.`);
            renderTable();
            return;
        }
    }
    components[index][field] = value;
    renderTable();
    updateTotalPowerDraw();
}

function removeComponent(index) {
    components.splice(index, 1);
    renderTable();
    updateTotalPowerDraw();
}

function updateTotalPowerDraw() {
    const powerByVoltage = { 230: 0, 120: 0, 48: 0, 24: 0, 12: 0, 5: 0 };

    components.forEach(component => {
        const calculatedPower = component.powerDraw * (component.percentage / 100) * component.amount;
        if (powerByVoltage.hasOwnProperty(component.voltage)) {
            powerByVoltage[component.voltage] += calculatedPower;
        }
    });

    document.getElementById('total-power-230V').innerText = `230V: ${powerByVoltage[230].toFixed(2)}W`;
    document.getElementById('total-power-120V').innerText = `120V: ${powerByVoltage[120].toFixed(2)}W`;
    document.getElementById('total-power-48V').innerText = `48V: ${powerByVoltage[48].toFixed(2)}W`;
    document.getElementById('total-power-24V').innerText = `24V: ${powerByVoltage[24].toFixed(2)}W`;
    document.getElementById('total-power-12V').innerText = `12V: ${powerByVoltage[12].toFixed(2)}W`;
    document.getElementById('total-power-5V').innerText = `5V: ${powerByVoltage[5].toFixed(2)}W`;
}

function saveCurrentBuild() {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(components));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "current_build.json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
}

function loadPreviousBuild() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = e => { 
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = event => {
            const data = JSON.parse(event.target.result);
            components.length = 0;
            data.forEach(component => components.push(component));
            renderTable();
            updateTotalPowerDraw();
        };
        reader.readAsText(file);
    };
    input.click();
}
