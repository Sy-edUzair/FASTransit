
function generateStopFields() {
    const numStops = document.getElementById("numStops").value;
    const stopsContainer = document.getElementById("stopsContainer");

    // Clear previous fields
    stopsContainer.innerHTML = "";

    // Generate input fields for each stop
    for (let i = 1; i <= numStops; i++) {
        const div = document.createElement("div");
        div.className = "col-xl-3 col-lg-6 col-12 form-group";
        div.innerHTML = `
                <label>Stop ${i}*</label>
                <input type="text" placeholder="Enter Stop ${i} Name" class="form-control">
            `;
        stopsContainer.appendChild(div);
    }
}


