//For flashed messages
const flashMessages = document.querySelectorAll('.success, .info, .error');
const delayInSeconds = 2; // Set the desired delay in seconds

flashMessages.forEach((message, index) => {
    setTimeout(() => {
        message.style.display = 'none';
    }, (index + 1) * delayInSeconds * 1000); // Convert seconds to milliseconds
});

// This is for pop up transacts
// ///////////////////////////////////
////////////////////////////////////

document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("send_mon_modal");
    const openModalBtn = document.getElementById("send_btn");
    const cancelBtn = document.getElementById("cancelBtn");
    const modalForm = document.getElementById("send_modalForm");

    openModalBtn.addEventListener("click", function() {
        modal.style.display = "block";
        modal.focus();
    });

    cancelBtn.addEventListener("click", function() {
        modal.style.display = "none";
    });

    modalForm.addEventListener("submit", function(event) {
        event.preventDefault();
        const input_email = document.getElementById("input_email").value;
        const input_amt = document.getElementById("input_amt").value;
        modal.style.display = "none";

        fetch('/try_send_mon', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `input_email=${encodeURIComponent(input_email)}&input_amt=${encodeURIComponent(input_amt)}`
        })
        .then(response => response.json())
        .then(data => { //check
            // console.log(data.message);  // Log the response message
            window.location.reload();
        })
        .catch(error => console.error('Error:', error));
    });

    window.addEventListener("click", function(event) {
        if (event.target !== modal && !modal.contains(event.target) && modal.style.display === "block") {
            modal.classList.add("flash");
            setTimeout(() => {
                modal.classList.remove("flash");
            }, 100);
        }
    });
});

// This is for Funding pop up
// ///////////////////////////////////
////////////////////////////////////

document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("fund_modal");
    const openModalBtn = document.getElementById("fundinput_amt");
    const cancelBtn = document.getElementById("cancelBtn");
    const modalForm = document.getElementById("fund_modalForm");

    openModalBtn.addEventListener("click", function() {
        modal.style.display = "block";
        modal.focus();
    });

    cancelBtn.addEventListener("click", function() {
        modal.style.display = "none";
    });

    modalForm.addEventListener("submit", function(event) {
        event.preventDefault();
        const input_amt = document.getElementById("fund_text_input_amt").value;
        modal.style.display = "none";

        fetch('/try-fund_acc', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `input_amt=${encodeURIComponent(input_amt)}`
        })
        .then(response => response.json())
        .then(data => {
            window.location.reload();
        })
        .catch(error => console.error('Error:', error));
    });

// Consider removing this fragment and the similar piece above, not sure if it works as expected
    window.addEventListener("click", function(event) {
        if (event.target !== modal && !modal.contains(event.target) && modal.style.display === "block") {
            modal.classList.add("flash");
            setTimeout(() => {
                modal.classList.remove("flash");
            }, 100);
        }
    });
});