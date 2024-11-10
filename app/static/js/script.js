// script.js

document.addEventListener("DOMContentLoaded", function () {
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatOutput = document.getElementById("chat-output");

    chatForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const query = chatInput.value;
        chatInput.value = "";

        // Append user query
        chatOutput.innerHTML += `<p><strong>You:</strong> ${query}</p>`;

        // Send query to the server
        const response = await fetch("/query", {
            method: "POST", headers: {
                "Content-Type": "application/json",
            }, body: JSON.stringify({query}),
        });

        const data = await response.json();
        const botResponse = data.response || "Sorry, I couldn't understand that.";

        // Append bot response
        chatOutput.innerHTML += `<p><strong>Bot:</strong> ${botResponse}</p>`;
        chatOutput.scrollTop = chatOutput.scrollHeight;
    });
});
