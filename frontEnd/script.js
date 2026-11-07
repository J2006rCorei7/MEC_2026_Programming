function ShowForm(){
    let form = document.getElementById("foodModal");
    if(!form.classList.contains("active")){
        form.addEventListener(escape, hideForm)
        form.classList.add("active");
    }
}


function hideForm(){
    if (document.getElementById("foodModal").classList.contains("active")){
        document.getElementById("foodModal").classList.remove("active");
    }
}


async function submit_form(event) {
    event.preventDefault();

    const form = document.getElementById("foodRequestForm");
    const formData = new FormData(form);

    const values = Object.fromEntries(formData.entries());

    // Convert numeric values
    const numberFields = [
        "people",
        "hotNeeded",
        "hotRemaining",
        "coldNeeded",
        "coldRemaining",
        "hours"
    ];

    numberFields.forEach(field => {
        values[field] = values[field] === ""
            ? null
            : Number(values[field]);
    });

    // Construct JSON payload
    const payload = {
        dest_name: values.destination,
        dest_type: values.type,
        num_people: values.people,
        address: values.address,
        hot_food_needed: values.hotNeeded,
        hot_food_available: values.hotRemaining,
        cold_food_needed: values.coldNeeded,
        cold_food_available: values.coldRemaining,
        delivery_deadline: values.hours,
        urgency_level: values.urgency
    };

    try {
        const response = await fetch("/api/request/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || "Request failed");
        }

        console.log("Server response:", result);

    } catch (error) {
        console.error("POST error:", error);
    }
}

document.getElementById("foodRequestForm")
    .addEventListener("submit", submit_form);