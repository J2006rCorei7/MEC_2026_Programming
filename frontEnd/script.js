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