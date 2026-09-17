const API_URL = window.CHILLIPROFIT_API_URL || 'http://127.0.0.1:8000';
const MAX_BYTES = 10 * 1024 * 1024;
const ALLOWED_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp']);

const leafInput = document.getElementById('leafInput');
const preview = document.getElementById('preview');
const uploadContent = document.getElementById('uploadContent');
const resultTitle = document.getElementById('resultTitle');
const resultText = document.getElementById('resultText');
const confidence = document.getElementById('confidence');
const confidenceBar = document.getElementById('confidenceBar');
const severity = document.getElementById('severity');
const zone = document.getElementById('zone');
const nextStep = document.getElementById('nextStep');
const resultCard = document.getElementById('resultCard');
const resultTop = resultCard?.querySelector('.result-top');

function setResultState(title, message, options = {}) {
  resultTitle.textContent = title;
  resultText.textContent = message;
  confidence.textContent = options.confidence == null ? '—' : `${options.confidence}%`;
  confidenceBar.style.width = options.confidence == null ? '0%' : `${Math.max(0, Math.min(100, options.confidence))}%`;
  severity.textContent = options.screeningBand || '—';
  zone.textContent = options.zone || '—';
  nextStep.textContent = options.nextStep || '—';

  if (resultTop) {
    resultTop.innerHTML = `<span class="status-dot"></span><span>${options.label || 'AI ANALYSIS'}</span><span class="demo-tag">${options.modelVersion || 'MODEL'}</span>`;
  }
}

leafInput.addEventListener('change', async () => {
  const file = leafInput.files?.[0];
  if (!file) return;

  if (!ALLOWED_TYPES.has(file.type)) {
    setResultState('Unsupported image', 'Please upload a JPG, PNG or WEBP image.', { label: 'UPLOAD ERROR', modelVersion: 'CHECK' });
    leafInput.value = '';
    return;
  }

  if (file.size > MAX_BYTES) {
    setResultState('Image too large', 'The image must be 10 MB or smaller.', { label: 'UPLOAD ERROR', modelVersion: 'CHECK' });
    leafInput.value = '';
    return;
  }

  const reader = new FileReader();
  reader.onload = event => {
    preview.src = event.target.result;
    preview.hidden = false;
    uploadContent.hidden = true;
  };
  reader.readAsDataURL(file);

  await analyzeLeaf(file);
});

async function analyzeLeaf(file) {
  setResultState('Analyzing image…', 'Uploading the leaf image to the ChilliProfit AI backend.', { label: 'AI ANALYSIS', modelVersion: 'MODEL', nextStep: 'Processing' });

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_URL}/api/analyze`, {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Analysis request failed.');

    if (data.status === 'prediction') {
      setResultState(data.title || 'Analysis complete', data.message || 'Model prediction generated.', {
        confidence: data.confidence,
        screeningBand: data.severity,
        zone: data.zone,
        nextStep: data.next_step,
        label: 'AI ANALYSIS',
        modelVersion: data.model_version || 'MODEL'
      });

      if (data.probabilities) {
        const probabilityText = Object.entries(data.probabilities)
          .sort(([, a], [, b]) => b - a)
          .map(([name, value]) => `${name.replaceAll('_', ' ')} ${value}%`)
          .join(' • ');
        resultText.textContent = `${data.message || 'Model prediction generated.'} Probabilities: ${probabilityText}.`;
      }
    } else {
      setResultState(data.title || 'Image received', data.message || 'The image was validated successfully.', {
        label: 'MODEL STATUS',
        modelVersion: data.model_version || 'SETUP',
        nextStep: data.next_step,
        screeningBand: data.severity,
        zone: data.zone
      });
    }
  } catch (error) {
    setResultState('Backend unavailable', `${error.message} Start the FastAPI server and try again.`, { label: 'CONNECTION ERROR', modelVersion: 'API', nextStep: 'Start API' });
  }
}

const yieldInput = document.getElementById('yieldInput');
const priceInput = document.getElementById('priceInput');
const costInput = document.getElementById('costInput');
const revenue = document.getElementById('revenue');
const net = document.getElementById('net');

function updateEconomics() {
  const y = Number(yieldInput.value) || 0;
  const p = Number(priceInput.value) || 0;
  const c = Number(costInput.value) || 0;
  const gross = y * p;
  const profit = gross - c;
  const money = value => `₹${Math.round(value).toLocaleString('en-IN')}`;
  revenue.textContent = money(gross);
  net.textContent = money(profit);
}

[yieldInput, priceInput, costInput].forEach(input => input.addEventListener('input', updateEconomics));
updateEconomics();

document.querySelectorAll('.zone').forEach(button => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.zone').forEach(z => z.style.outline = 'none');
    button.style.outline = '3px solid rgba(185,223,101,.85)';
    resultText.textContent = `${button.dataset.zone} selected. Capture a leaf image from this zone for disease screening.`;
    zone.textContent = button.dataset.zone;
  });
});
