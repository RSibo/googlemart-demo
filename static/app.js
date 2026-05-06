const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const magicIcon = document.getElementById('magic-icon');
const settingsBtn = document.getElementById('settings-btn');
const settingsContainer = document.getElementById('settings-container');
const saveSettingsBtn = document.getElementById('save-settings-btn');
const accessTokenInput = document.getElementById('access-token');
const projectIdInput = document.getElementById('project-id');
const locationInput = document.getElementById('location');
const modelIdInput = document.getElementById('model-id');
const voiceSelect = document.getElementById('voice-select');
const avatarSelect = document.getElementById('avatar-select');
const avatarFrame = document.getElementById('avatar-frame');

// Connect to WebSocket
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${window.location.host}/ws`;
const socket = new WebSocket(wsUrl);

socket.onopen = () => {
    console.log('Connected to WebSocket');
    sendSetup();
};

function sendSetup() {
    const settings = loadSettings();
    if (settings.accessToken) {
        socket.send(JSON.stringify({
            type: 'setup',
            content: settings
        }));
    }
}

function loadSettings() {
    return {
        accessToken: localStorage.getItem('accessToken') || '',
        projectId: localStorage.getItem('projectId') || '',
        location: localStorage.getItem('location') || 'us-central1',
        modelId: localStorage.getItem('modelId') || 'gemini-3.1-flash-live-preview',
        voice: localStorage.getItem('voice') || 'Puck',
        avatar: localStorage.getItem('avatar') || 'Ben'
    };
}

function populateSettings() {
    const settings = loadSettings();
    accessTokenInput.value = settings.accessToken;
    projectIdInput.value = settings.projectId;
    locationInput.value = settings.location;
    modelIdInput.value = settings.modelId;
    voiceSelect.value = settings.voice;
    avatarSelect.value = settings.avatar;
}

populateSettings();

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'text') {
        appendMessage('chef', data.content);
    } else if (data.type === 'error') {
        appendMessage('chef', `Error: ${data.content}`);
    } else if (data.type === 'video') {
        avatarFrame.src = `data:image/jpeg;base64,${data.content}`;
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

settingsBtn.addEventListener('click', () => {
    if (settingsContainer.style.display === 'none' || settingsContainer.style.display === '') {
        settingsContainer.style.display = 'flex';
        chatContainer.style.display = 'none';
        document.getElementById('input-container').style.display = 'none';
        document.getElementById('avatar-display').style.display = 'none';
    } else {
        settingsContainer.style.display = 'none';
        chatContainer.style.display = 'flex';
        document.getElementById('input-container').style.display = 'flex';
        document.getElementById('avatar-display').style.display = 'flex';
    }
});

saveSettingsBtn.addEventListener('click', () => {
    localStorage.setItem('accessToken', accessTokenInput.value);
    localStorage.setItem('projectId', projectIdInput.value);
    localStorage.setItem('location', locationInput.value);
    localStorage.setItem('modelId', modelIdInput.value);
    localStorage.setItem('voice', voiceSelect.value);
    localStorage.setItem('avatar', avatarSelect.value);
    
    settingsContainer.style.display = 'none';
    chatContainer.style.display = 'flex';
    document.getElementById('input-container').style.display = 'flex';
    document.getElementById('avatar-display').style.display = 'flex';
    
    sendSetup();
});

// Cart functionality
let cart = [];
const cartCountSpan = document.getElementById('cart-count');

document.querySelectorAll('.add-btn').forEach(button => {
    button.addEventListener('click', () => {
        const sku = button.getAttribute('data-sku');
        cart.push(sku);
        cartCountSpan.textContent = cart.length;
        console.log(`Added to cart: ${sku}`);
    });
});
