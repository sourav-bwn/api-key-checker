const PROVIDERS = [
  {
    name: 'OpenAI',
    testKey: key => key.startsWith('sk-'),
    endpoint: 'https://api.openai.com/v1/models',
    headers: key => ({ 'Authorization': `Bearer ${key}` }),
    validate: async res => res.status !== 401 && res.status !== 403,
  },
  {
    name: 'Anthropic',
    testKey: key => key.startsWith('sk-ant-'),
    endpoint: 'https://api.anthropic.com/v1/messages',
    headers: key => ({
      'x-api-key': key,
      'anthropic-version': '2023-06-01',
      'Content-Type': 'application/json',
    }),
    validate: async (res, body) => {
      if (res.status === 401 || res.status === 403) return false;
      if (res.status === 400) return true;
      return res.ok;
    },
  },
  {
    name: 'Google Gemini',
    testKey: key => key.startsWith('AIza'),
    endpoint: key => `https://generativelanguage.googleapis.com/v1/models?key=${key}`,
    headers: () => ({}),
    validate: async res => res.status !== 403 && res.status !== 401,
  },
  {
    name: 'Groq',
    testKey: key => key.startsWith('gsk_'),
    endpoint: 'https://api.groq.com/openai/v1/models',
    headers: key => ({ 'Authorization': `Bearer ${key}` }),
    validate: async res => res.status !== 401 && res.status !== 403,
  },
  {
    name: 'Hugging Face',
    testKey: key => key.startsWith('hf_'),
    endpoint: 'https://huggingface.co/api/models?limit=1',
    headers: key => ({ 'Authorization': `Bearer ${key}` }),
    validate: async res => res.status !== 401 && res.status !== 403,
  },
  {
    name: 'Cohere',
    testKey: key => key.startsWith('co'),
    endpoint: 'https://api.cohere.ai/v1/models',
    headers: key => ({
      'Authorization': `Bearer ${key}`,
      'Content-Type': 'application/json',
    }),
    validate: async res => res.status !== 401 && res.status !== 403,
  },
  {
    name: 'Together AI',
    testKey: key => key.startsWith('tgp-'),
    endpoint: 'https://api.together.xyz/v1/models',
    headers: key => ({ 'Authorization': `Bearer ${key}` }),
    validate: async res => res.status !== 401 && res.status !== 403,
  },
  {
    name: 'Mistral',
    testKey: key => key.startsWith('xi-'),
    endpoint: 'https://api.mistral.ai/v1/models',
    headers: key => ({ 'Authorization': `Bearer ${key}` }),
    validate: async res => res.status !== 401 && res.status !== 403,
  },
  {
    name: 'Perplexity',
    testKey: key => key.startsWith('pplx-'),
    endpoint: 'https://api.perplexity.ai/models',
    headers: key => ({ 'Authorization': `Bearer ${key}` }),
    validate: async res => res.status !== 401 && res.status !== 403,
  },
  {
    name: 'Replicate',
    testKey: key => key.startsWith('r8_'),
    endpoint: 'https://api.replicate.com/v1/models',
    headers: key => ({ 'Authorization': `Key ${key}` }),
    validate: async res => res.status !== 401 && res.status !== 403,
  },
  {
    name: 'ElevenLabs',
    testKey: key => key.startsWith('sk_'),
    endpoint: 'https://api.elevenlabs.io/v1/user',
    headers: key => ({ 'xi-api-key': key }),
    validate: async res => res.status !== 401 && res.status !== 403,
  },
  {
    name: 'OpenRouter',
    testKey: key => key.startsWith('sk-or-'),
    endpoint: 'https://openrouter.ai/api/v1/models',
    headers: key => ({ 'Authorization': `Bearer ${key}` }),
    validate: async res => res.status !== 401 && res.status !== 403,
  },
  {
    name: 'GitHub',
    testKey: key => key.startsWith('ghp_') || key.startsWith('github_pat_'),
    endpoint: 'https://api.github.com/user',
    headers: key => ({ 'Authorization': `Bearer ${key}` }),
    validate: async res => res.status !== 401 && res.status !== 403,
  },
  {
    name: 'GitLab',
    testKey: key => key.startsWith('glpat-'),
    endpoint: 'https://gitlab.com/api/v4/user',
    headers: key => ({ 'Authorization': `Bearer ${key}` }),
    validate: async res => res.status !== 401 && res.status !== 403,
  },
  {
    name: 'Stability AI',
    testKey: key => /^sk-[A-Za-z0-9]{20,}$/.test(key),
    endpoint: 'https://api.stability.ai/v1/user/account',
    headers: key => ({ 'Authorization': `Bearer ${key}` }),
    validate: async res => res.status !== 401 && res.status !== 403,
  },
  {
    name: 'DeepSeek',
    testKey: key => key.startsWith('sk-'),
    endpoint: 'https://api.deepseek.com/v1/models',
    headers: key => ({ 'Authorization': `Bearer ${key}` }),
    validate: async res => res.status !== 401 && res.status !== 403,
  },
  {
    name: 'NVIDIA',
    testKey: key => key.startsWith('nvapi-'),
    endpoint: 'https://integrate.api.nvidia.com/v1/chat/completions',
    headers: key => ({
      'Authorization': `Bearer ${key}`,
      'Content-Type': 'application/json',
    }),
    validate: async res => res.status !== 401 && res.status !== 403,
    body: { model: 'moonshotai/kimi-k2.6', messages: [{ role: 'user', content: 'test' }], max_tokens: 1 },
  },
];

const chatMessages = document.getElementById('chatMessages');
const keyInput = document.getElementById('keyInput');
const sendBtn = document.getElementById('sendBtn');
const providerTag = document.getElementById('providerTag');

let isChecking = false;

keyInput.addEventListener('input', () => {
  const val = keyInput.value.trim();
  sendBtn.disabled = !val || isChecking;
  detectProvider(val);
});

keyInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !sendBtn.disabled) sendKey();
});

sendBtn.addEventListener('click', sendKey);

function detectProvider(key) {
  if (!key) {
    providerTag.textContent = 'Paste an API key to auto-detect provider';
    return;
  }
  const match = PROVIDERS.find(p => p.testKey(key));
  providerTag.textContent = match
    ? `Detected: ${match.name}`
    : 'Unknown provider format — will try common endpoints';
}

function addMessage(text, type = 'bot', result = null) {
  const div = document.createElement('div');
  div.className = `message ${type}`;

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.innerHTML = type === 'bot'
    ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>'
    : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>';

  const content = document.createElement('div');
  content.className = 'msg-content';

  const textDiv = document.createElement('div');
  textDiv.className = 'msg-text';
  textDiv.textContent = text;
  content.appendChild(textDiv);

  if (result) {
    const resultDiv = document.createElement('div');
    resultDiv.className = `msg-result ${result.status}`;
    resultDiv.innerHTML = `<strong>${result.icon} ${result.title}</strong>`;
    if (result.details) {
      const detailsDiv = document.createElement('div');
      detailsDiv.className = 'msg-details';
      detailsDiv.innerHTML = result.details;
      content.appendChild(detailsDiv);
    }
    content.appendChild(resultDiv);
  }

  div.appendChild(avatar);
  div.appendChild(content);
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addTyping() {
  const div = document.createElement('div');
  div.className = 'message bot';
  div.id = 'typingIndicator';
  div.innerHTML = `
    <div class="msg-avatar">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
    </div>
    <div class="msg-content">
      <div class="msg-text">
        <div class="typing-dots"><span></span><span></span><span></span></div>
      </div>
    </div>
  `;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

async function sendKey() {
  const key = keyInput.value.trim();
  if (!key || isChecking) return;

  isChecking = true;
  sendBtn.disabled = true;

  addMessage(key, 'user');

  keyInput.value = '';
  providerTag.textContent = '';

  addTyping();

  const matchedProviders = PROVIDERS.filter(p => p.testKey(key));

  if (matchedProviders.length === 0) {
    removeTyping();
    addMessage('Could not auto-detect the provider from your key format. Try these common patterns:', 'bot');
    addMessage('OpenAI: sk-...\nAnthropic: sk-ant-...\nGroq: gsk_...\nGoogle: AIza...', 'bot');
    isChecking = false;
    return;
  }

  for (const provider of matchedProviders) {
    removeTyping();

    try {
      const endpoint = typeof provider.endpoint === 'function' ? provider.endpoint(key) : provider.endpoint;
      const fetchOpts = {
        method: provider.body ? 'POST' : 'GET',
        headers: provider.headers(key),
        signal: AbortSignal.timeout(10000),
      };
      if (provider.body) fetchOpts.body = JSON.stringify(provider.body);
      const response = await fetch(endpoint, fetchOpts);

      const valid = await provider.validate(response);

      if (valid) {
        addMessage(`Testing ${provider.name}...`, 'bot', {
          status: 'valid',
          icon: '✅',
          title: `${provider.name} key is VALID`,
          details: `Status: ${response.status} ${response.statusText}<br>Provider: ${provider.name}<br>Endpoint: <code>${endpoint}</code>`,
        });
        chatMessages.scrollTop = chatMessages.scrollHeight;
      } else {
        addMessage(`Testing ${provider.name}...`, 'bot', {
          status: 'invalid',
          icon: '❌',
          title: `${provider.name} key is INVALID`,
          details: `Status: ${response.status} ${response.statusText}<br>Provider: ${provider.name}<br>Endpoint: <code>${endpoint}</code>`,
        });
      }
    } catch (err) {
      const isCors = err.message === 'Failed to fetch' || err.name === 'TypeError';
      if (isCors) {
        addMessage(`Testing ${provider.name}...`, 'bot', {
          status: 'error',
          icon: '🔒',
          title: `${provider.name} blocked by browser CORS`,
          details: `This API doesn't allow browser-based checks.<br><br>Run this in your terminal instead:<br><code>curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${key.slice(0,8)}..." ${typeof provider.endpoint === 'function' ? provider.endpoint(key) : provider.endpoint}</code>`,
        });
      } else {
        addMessage(`Testing ${provider.name}...`, 'bot', {
          status: 'error',
          icon: '⚠️',
          title: `Could not verify ${provider.name} key`,
          details: `Error: ${err.message}<br>Provider: ${provider.name}`,
        });
      }
    }
  }

  removeTyping();
  isChecking = false;
  sendBtn.disabled = !keyInput.value.trim();
}
