// File: static/script.js

document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const userMessageInput = document.getElementById('user-message');
            const message = userMessageInput.value.trim();
            if (message !== '') {
                appendMessage('You', message);
                userMessageInput.value = '';
                sendMessage(message);
            }
        });
    }
});

function sendMessage(message) {
    fetch('/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: message, session_id: sessionId })
    })
        .then(response => response.json())
        .then(data => {
            if (data.response) {
                appendMessage('Chatbot', data.response);
            } else if (data.error) {
                appendMessage('Error', data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function appendMessage(sender, message) {
    const chatWindow = document.getElementById('chat-window');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    if (sender === 'You') {
        messageElement.classList.add('user-message');
    } else {
        messageElement.classList.add('bot-message');
    }
    messageElement.textContent = `${sender}: ${message}`;
    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function loadChatHistory(sessionId) {
    fetch(`/get_chat_history/${sessionId}`)
        .then(response => response.json())
        .then(data => {
            const chatWindow = document.getElementById('chat-window');
            chatWindow.innerHTML = '';
            data.forEach(item => {
                appendMessage('You', item.query);
                appendMessage('Chatbot', item.response);
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function loadChatSessions() {
    fetch('/get_chat_sessions')
        .then(response => response.json())
        .then(data => {
            const sessionsList = document.getElementById('chat-sessions-list');
            sessionsList.innerHTML = '';
            data.forEach(session => {
                const listItem = document.createElement('li');
                const link = document.createElement('a');
                link.href = `/chat/${session.id}`;
                link.textContent = session.title;
                listItem.appendChild(link);
                sessionsList.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
