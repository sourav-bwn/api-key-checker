const providers = [
  { name: 'OpenAI', keyPrefix: 'sk-', color: '#10a37f' },
  { name: 'Anthropic', keyPrefix: 'sk-ant-', color: '#d4a574' },
  { name: 'Google Gemini', keyPrefix: 'AIza', color: '#4285f4' },
  { name: 'Groq', keyPrefix: 'gsk_', color: '#f97316' },
  { name: 'Hugging Face', keyPrefix: 'hf_', color: '#fbbf24' },
  { name: 'Cohere', keyPrefix: 'co', color: '#d18ee2' },
  { name: 'Together AI', keyPrefix: 'tgp-', color: '#7c3aed' },
  { name: 'Mistral', keyPrefix: 'xi-', color: '#ff6f00' },
  { name: 'DeepSeek', keyPrefix: 'sk-', color: '#4f46e5' },
  { name: 'Perplexity', keyPrefix: 'pplx-', color: '#22c55e' },
  { name: 'Replicate', keyPrefix: 'r8_', color: '#38bdf8' },
  { name: 'Stability AI', keyPrefix: 'sk-', color: '#a855f7' },
  { name: 'ElevenLabs', keyPrefix: 'sk_', color: '#0ea5e9' },
  { name: 'OpenRouter', keyPrefix: 'sk-or-', color: '#f59e0b' },
  { name: 'GitHub', keyPrefix: 'ghp_', color: '#6e40c9' },
  { name: 'GitLab', keyPrefix: 'glpat-', color: '#e24329' },
  { name: 'Hume AI', keyPrefix: 'sk-', color: '#f472b6' },
  { name: 'Vapi', keyPrefix: 'vapi-', color: '#06b6d4' },
  { name: 'AssemblyAI', keyPrefix: 'aa-', color: '#14b8a6' },
  { name: 'RunPod', keyPrefix: 'rpa-', color: '#8b5cf6' },
  { name: 'NVIDIA', keyPrefix: 'nvapi-', color: '#76b900' },
];

const grid = document.getElementById('providersGrid');

providers.forEach(p => {
  const chip = document.createElement('div');
  chip.className = 'provider-chip';
  chip.innerHTML = `
    <span class="provider-dot" style="background:${p.color}"></span>
    <span>${p.name}</span>
    <span style="color:var(--text-muted);font-size:0.75rem;font-family:var(--font-mono)">${p.keyPrefix}...</span>
  `;
  grid.appendChild(chip);
});
