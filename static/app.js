const form = document.querySelector('#chat-form');
const input = document.querySelector('#message');
const conversation = document.querySelector('#conversation');
const counter = document.querySelector('#char-count');
const sendButton = document.querySelector('.send-button');
const statusDot = document.querySelector('#status-dot');
const statusLabel = document.querySelector('#status-label');
const statusDetail = document.querySelector('#status-detail');

function updateCount() {
  counter.textContent = `${input.value.length} / 4000`;
}

function addMessage(role, text, label, timestamp = '') {
  const article = document.createElement('article');
  article.className = `message ${role === 'user' ? 'user-message' : 'assistant-message'}`;
  article.innerHTML = `
    <div class="avatar">${role === 'user' ? 'YOU' : 'TC'}</div>
    <div class="bubble">
      <span class="message-label">${label}</span>
      <p></p>
      <time>${timestamp || (role === 'user' ? 'Submitted for analysis' : 'Response received')}</time>
    </div>`;
  article.querySelector('p').textContent = text;
  conversation.appendChild(article);
  article.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function checkHealth() {
  try {
    const response = await fetch('/health');
    const data = await response.json();
    if (response.ok && data.status === 'ok') {
      statusDot.className = 'status-dot online';
      statusLabel.textContent = 'Ollama online';
      statusDetail.textContent = `${data.models.length} local model(s) visible`;
    } else {
      throw new Error('Ollama unavailable');
    }
  } catch {
    statusDot.className = 'status-dot offline';
    statusLabel.textContent = 'Ollama unavailable';
    statusDetail.textContent = 'Start the local service to chat';
  }
}

input.addEventListener('input', updateCount);
document.querySelectorAll('[data-prompt]').forEach((button) => {
  button.addEventListener('click', () => {
    input.value = button.dataset.prompt;
    updateCount();
    input.focus();
  });
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  addMessage('user', message, 'You');
  input.value = '';
  updateCount();
  sendButton.disabled = true;
  sendButton.querySelector('span').textContent = 'Thinking';

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'The request failed.');
    addMessage('assistant', data.message, 'TechCorp Assistant', 'Model response received');
  } catch (error) {
    addMessage('assistant', error.message, 'Request error', 'Check the terminal and Ollama service');
  } finally {
    sendButton.disabled = false;
    sendButton.querySelector('span').textContent = 'Send';
  }
});

updateCount();
checkHealth();
