const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const magicIcon = document.getElementById('magic-icon');

// Connect to WebSocket
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${window.location.host}/ws`;
const socket = new WebSocket(wsUrl);

socket.onopen = () => {
    console.log('Connected to WebSocket');
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'text') {
        appendMessage('chef', data.content);
    } else if (data.type === 'error') {
        appendMessage('chef', `Error: ${data.content}`);
    }
};

socket.onclose = () => {
    console.log('WebSocket connection closed');
};

function appendMessage(sender, content) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');
    msgDiv.classList.add(sender === 'user' ? 'user-message' : 'chef-message');
    
    if (sender === 'chef') {
        const img = document.createElement('img');
        img.src = '/static/avatar.png';
        img.classList.add('avatar');
        msgDiv.appendChild(img);
        
        const textSpan = document.createElement('span');
        textSpan.innerHTML = content.replace(/\n/g, '<br>'); // Simple markdown-like newline handling
        msgDiv.appendChild(textSpan);
    } else {
        msgDiv.textContent = content;
    }
    
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function sendMessage() {
    const text = userInput.value.trim();
    if (text && socket.readyState === WebSocket.OPEN) {
        appendMessage('user', text);
        socket.send(JSON.stringify({ content: text }));
        userInput.value = '';
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

magicIcon.addEventListener('click', () => {
    const chatFlyout = document.getElementById('chat-flyout');
    if (chatFlyout.style.display === 'none' || chatFlyout.style.display === '') {
        chatFlyout.style.display = 'flex';
        // Send auto message if chat is empty (only greeting present)
        if (chatContainer.children.length <= 1) {
            userInput.value = "What can I make with my cart?";
            sendMessage();
        }
    } else {
        chatFlyout.style.display = 'none';
    }
});
