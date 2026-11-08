function ShowForm(){
    let form = document.getElementById("foodModal");
    if(!form.classList.contains("active")){
        form.classList.add("active");
    }
}


function hideForm(){
    if (document.getElementById("foodModal").classList.contains("active")){
        document.getElementById("foodModal").classList.remove("active");
    }
}

document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
        hideForm();
    }
});

document.addEventListener("click", function(event) {
    const modal = document.getElementById("foodModal");
    if (event.target === modal) {
        hideForm();
    }
});


async function submit_form(event) {
    event.preventDefault()
    const form = document.getElementById("foodRequestForm");
    const formData = new FormData(form);

    // Convert form fields into the API's expected JSON format
    const dropdown = form.querySelector('select[name="destination"]');

    const destName = dropdown.options[dropdown.selectedIndex].text;
    const data = {
        dest_name: destName,
        dest_type: formData.get("type"),
        num_people: Number(formData.get("people")) || 0,
        address: formData.get("address"),

        hot_food_needed: Number(formData.get("hotNeeded")) || 0,
        hot_food_available: Number(formData.get("hotRemaining")) || 0,

        cold_food_needed: Number(formData.get("coldNeeded")) || 0,
        cold_food_available: Number(formData.get("coldRemaining")) || 0,

        delivery_deadline: Number(formData.get("hours")) || 0,
        urgency_level: formData.get("urgency")
    };

    try {
        const response = await fetch("/api/request/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                highlightRoads(data.path);
                hideForm();
            });
    }catch (e){
        console.log(e);
    }
}


async function loadRequests() {
    try {
        const response = await fetch("/api/request");

        if (!response.ok) {
            throw new Error("Failed to retrieve requests");
        }

        const data = await response.json();

        const tableBody = document.getElementById("requestsTableBody");

        tableBody.innerHTML = "";

        data.forEach(request => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${request.id}</td>
                <td>${request.dest_name}</td>
                <td>${request.dest_type}</td>
                <td>${request.num_people}</td>
                <td>${request.address}</td>
                <td>${request.hot_food_needed}</td>
            `;

            tableBody.appendChild(row);
        });

    } catch (error) {
        console.error("Error loading requests:", error);
    }
}

// Load table when page loads
document.addEventListener("DOMContentLoaded", loadRequests);
