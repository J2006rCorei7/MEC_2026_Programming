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
    event.preventDefault()
    const form = document.getElementById("foodRequestForm");
    const formData = new FormData(form);

    // Convert form fields into the API's expected JSON format
    const data = {
        dest_name: formData.get("destination"),
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
        const response = await fetch("http://127.0.0.1:5000/api/request/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Failed to submit request");
        }

        console.log("Request submitted:", result);
        alert("Food request submitted successfully!");
        hideForm();

    } catch (error) {
        console.error("Submission error:", error);
        alert("Error submitting request: " + error.message);
    }
}