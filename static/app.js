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
        projectId: localStorage.getItem('projectId') || 'cloud-llm-preview1',
        location: localStorage.getItem('location') || 'us-central1',
        modelId: localStorage.getItem('modelId') || 'gemini-3.1-flash-live-preview-04-2026',
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
let cart = {}; // SKU -> quantity
const cartCountSpan = document.getElementById('cart-count');
const cartDisplay = document.getElementById('cart-display');
const cartFlyout = document.getElementById('cart-flyout');
const cartItemsContainer = document.getElementById('cart-items-container');

// Scrape product data from DOM
const productsData = {};
document.querySelectorAll('.product-card').forEach(card => {
    const sku = card.querySelector('.add-btn').getAttribute('data-sku');
    const name = card.querySelector('.product-name').textContent;
    const price = parseFloat(card.querySelector('.product-price').textContent.replace('$', ''));
    productsData[sku] = { name, price };
});

function updateCartUI() {
    let totalCount = 0;
    cartItemsContainer.innerHTML = '';
    let hasItems = false;
    
    for (const sku in cart) {
        const qty = cart[sku];
        if (qty > 0) {
            hasItems = true;
            totalCount += qty;
            const item = productsData[sku];
            
            const itemDiv = document.createElement('div');
            itemDiv.classList.add('cart-item');
            
            const infoDiv = document.createElement('div');
            infoDiv.innerHTML = `
                <div style="font-size:14px; font-weight:bold;">${item ? item.name : sku}</div>
                <div style="font-size:12px; color:#666;">$${item ? item.price.toFixed(2) : '0.00'} each</div>
            `;
            itemDiv.appendChild(infoDiv);
            
            const select = document.createElement('select');
            for (let i = 0; i <= 10; i++) {
                const option = document.createElement('option');
                option.value = i;
                option.textContent = i;
                if (i === qty) {
                    option.selected = true;
                }
                select.appendChild(option);
            }
            
            select.addEventListener('change', (e) => {
                const newQty = parseInt(e.target.value);
                if (newQty === 0) {
                    delete cart[sku];
                } else {
                    cart[sku] = newQty;
                }
                updateCartUI();
                sendCartToChef();
            });
            
            itemDiv.appendChild(select);
            cartItemsContainer.appendChild(itemDiv);
        }
    }
    
    cartCountSpan.textContent = totalCount;
    
    if (!hasItems) {
        cartItemsContainer.innerHTML = '<div class="cart-item">No items in cart</div>';
    }
}

function sendCartToChef() {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            type: 'cart_update',
            content: cart
        }));
    }
}

cartDisplay.addEventListener('click', () => {
    if (cartFlyout.style.display === 'none' || cartFlyout.style.display === '') {
        cartFlyout.style.display = 'flex';
    } else {
        cartFlyout.style.display = 'none';
    }
});

document.querySelectorAll('.add-btn').forEach(button => {
    button.addEventListener('click', () => {
        const sku = button.getAttribute('data-sku');
        if (cart[sku]) {
            cart[sku] = Math.min(cart[sku] + 1, 10);
        } else {
            cart[sku] = 1;
        }
        updateCartUI();
        sendCartToChef();
        console.log(`Added to cart: ${sku}`);
        
        // Open cart panel automatically on first add
        if (Object.keys(cart).length === 1 && cart[sku] === 1) {
             cartFlyout.style.display = 'flex';
        }
    });
});

// Initial UI sync
updateCartUI();

// Update socket.onopen to also send initial cart
const originalOnOpen = socket.onopen;
socket.onopen = () => {
    if (originalOnOpen) originalOnOpen();
    sendCartToChef();
};
