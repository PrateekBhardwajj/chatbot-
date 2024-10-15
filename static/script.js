document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const chatForm = document.getElementById('chat-form');
    const chatBox = document.getElementById('chat-box');
    const loginContainer = document.getElementById('login-container');
    const chatContainer = document.getElementById('chat-container');
    const logoutButton = document.getElementById('logout');

    logoutButton.addEventListener("click", () => {
        localStorage.clear();
        chatContainer.style.display = 'none';
        loginContainer.style.display = 'flex';
        window.location.reload();
    })

    if (localStorage.getItem('token')) {
        logoutButton.style.display = "flex"
    } else {
        logoutButton.style.display = "none"
    }

    if (localStorage.getItem('token')) {
        chatContainer.style.display = 'block';
        loginContainer.style.display = 'none';
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();
        if (response.ok) {
            localStorage.setItem("token", data.access_token)
            loginContainer.style.display = 'none';
            chatContainer.style.display = 'block';
            window.location.reload();
        } else {
            alert(data.msg);
        }
    });

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = document.getElementById('message');
        const persona = document.getElementById('persona');

        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ message: message.value, persona: persona.value })
        });

        const data = await response.json();
        if (response.ok) {
            chatBox.innerHTML += `<div class="message user-message">User: ${message.value}</div>`;
            chatBox.innerHTML += `<div class="message bot-message">Bot: ${data.response}</div>`;
            message.value = '';
        } else {
            console.log(data.error);
            alert(data.error);
        }
    });
});