// Path: static/js/script.js

// Generate or retrieve a unique user_id
function getUserId() {
    let userId = localStorage.getItem('user_id');
    if (!userId) {
        userId = generateUUID();
        localStorage.setItem('user_id', userId);
    }
    return userId;
}

function generateUUID() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
}

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

let currentSessionId = null;

// Start a New Chat Session
function startNewChat() {
    const userId = getUserId();
    currentSessionId = null;
    localStorage.removeItem('currentSessionId');
    document.getElementById('chat-window').innerHTML = '';  // Clear chat window
    fetch('/start_new_chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => response.json())
    .then(data => {
        currentSessionId = data.session_id;
        localStorage.setItem('currentSessionId', currentSessionId);
        const newChatMessage = '<div class="message bot-message">New chat session started. How can I help you?</div>';
        document.getElementById('chat-window').innerHTML = newChatMessage;
        loadChatHistory();
    })
    .catch(error => console.error('Error starting new chat session:', error));
}

// Handle Enter Key to Send Message
function handleEnterKey(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Send Message to the Chatbot
function sendMessage() {
    const userId = getUserId();
    if (!currentSessionId) {
        alert('Please start a new chat session first.');
        return;
    }
    const userInput = document.getElementById('user-input');
    const query = userInput.value;
    if (!query) return;

    const userMessage = `<div class="message user-message">${query}</div>`;
    document.getElementById('chat-window').innerHTML += userMessage;
    userInput.value = '';

    fetch('/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, user_id: userId, session_id: currentSessionId })
    })
    .then(response => response.json())
    .then(data => {
        let botMessageContent = '';
        if (data.error) {
            botMessageContent = data.error;
        } else {
            if (data.title) {
                botMessageContent += `<strong>${data.title}</strong><br>`;
            }
            if (data.description) {
                botMessageContent += `${data.description}<br>`;
            }
            if (data.url) {
                botMessageContent += `<a href="${data.url}" target="_blank">${data.url}</a><br>`;
            }
            if (data.source) {
                botMessageContent += `<em>Source: ${data.source}</em>`;
            }
        }
        const botResponse = `<div class="message bot-message">${botMessageContent}</div>`;
        document.getElementById('chat-window').innerHTML += botResponse;
        document.getElementById('chat-window').scrollTop = document.getElementById('chat-window').scrollHeight;
    })
    .catch(error => console.error('Error sending message:', error));
}

// Load Chat History into Sidebar
function loadChatHistory() {
    const userId = getUserId();
    fetch(`/get_chat_history?user_id=${userId}`, { method: 'GET' })
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
    currentSessionId = sessionId;
    localStorage.setItem('currentSessionId', currentSessionId);

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

    // Load the current chat session if one is stored
    currentSessionId = localStorage.getItem('currentSessionId');
    if (currentSessionId) {
        loadChatSession(currentSessionId);
    } else {
        // Optionally start a new chat session automatically
        startNewChat();
    }
};
