// path: static/js/script.js

// Collapse the sidebar by default on page load
document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.add('collapsed');
});

// Toggle Sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('collapsed');
}

// Display Upload Modal
function showUploadModal() {
    document.getElementById('upload-modal').style.display = 'block';
}

// Close Upload Modal
function closeUploadModal() {
    document.getElementById('upload-modal').style.display = 'none';
}

// Start a New Chat Session
function startNewChat() {
    document.getElementById('chat-window').innerHTML = '';  // Clear chat window
    fetch('/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: '', user_id: 'new_user' })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('chat-window').innerHTML = '<p>New chat session started. How can I help you?</p>';
    })
    .catch(error => console.error('Error starting new chat session:', error));
}

// Send Message to the Chatbot
function sendMessage() {
    const userInput = document.getElementById('user-input');
    const query = userInput.value;
    if (!query) return;

    const userMessage = `<div class="message user-message">${query}</div>`;
    document.getElementById('chat-window').innerHTML += userMessage;
    userInput.value = '';

    fetch('/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, user_id: 'default_user' })  // Replace 'default_user' with dynamic user ID as needed
    })
    .then(response => response.json())
    .then(data => {
        const botResponse = `<div class="message bot-message">${data.response || data.error}</div>`;
        document.getElementById('chat-window').innerHTML += botResponse;
        document.getElementById('chat-window').scrollTop = document.getElementById('chat-window').scrollHeight;
    })
    .catch(error => console.error('Error sending message:', error));
}

// Load Chat History into Sidebar
function loadChatHistory() {
    fetch('/get_chat_history', { method: 'GET' })
    .then(response => response.json())
    .then(histories => {
        const historyList = document.getElementById('chat-history-list');
        historyList.innerHTML = '';

        histories.forEach(history => {
            const historyItem = document.createElement('button');
            historyItem.className = 'history-item';
            historyItem.textContent = history.title;
            historyItem.onclick = () => loadChatSession(history.session_id);
            historyList.appendChild(historyItem);
        });
    })
    .catch(error => console.error('Error loading chat history:', error));
}

// Load Specific Chat Session
function loadChatSession(sessionId) {
    fetch(`/get_chat_session?session_id=${sessionId}`, { method: 'GET' })
    .then(response => response.json())
    .then(messages => {
        const chatWindow = document.getElementById('chat-window');
        chatWindow.innerHTML = '';
        messages.forEach(message => {
            const messageClass = message.sender === 'user' ? 'user-message' : 'bot-message';
            const chatMessage = `<div class="message ${messageClass}">${message.text}</div>`;
            chatWindow.innerHTML += chatMessage;
        });
        chatWindow.scrollTop = chatWindow.scrollHeight;
    })
    .catch(error => console.error('Error loading chat session:', error));
}

// Upload Files for Processing
function uploadFiles() {
    const formData = new FormData(document.getElementById('upload-form'));
    document.getElementById('upload-status').innerText = 'Uploading...';

    fetch('/upload_files', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('upload-status').innerText = data.message;
        if (data.success) {
            closeUploadModal();
            alert('Files uploaded and processed successfully.');
            startNewChat();  // Optionally start a new chat after successful upload
        } else {
            alert('File processing failed. Please check your files and try again.');
        }
    })
    .catch(error => {
        document.getElementById('upload-status').innerText = 'Error uploading files.';
        console.error('Error uploading files:', error);
    });
}

// Load chat history on page load
window.onload = function() {
    loadChatHistory();

    // Ensure the sidebar is collapsed by default
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.add('collapsed');
};
