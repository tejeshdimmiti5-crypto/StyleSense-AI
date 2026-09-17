const API_URL = window.CHILLIPROFIT_API_URL || 'http://127.0.0.1:8000';

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

leafInput.addEventListener('change', async () => {
  const file = leafInput.files?.[0];
  if (!file) return;

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
  resultTitle.textContent = 'Analyzing image…';
  resultText.textContent = 'Uploading the leaf image to the ChilliProfit AI backend.';
  confidence.textContent = '—';
  confidenceBar.style.width = '0%';
  severity.textContent = '—';
  zone.textContent = '—';
  nextStep.textContent = 'Processing';

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_URL}/api/analyze`, {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Analysis request failed.');

    resultTitle.textContent = data.title || 'Analysis complete';
    resultText.textContent = data.message || 'No additional analysis message was returned.';
    confidence.textContent = data.confidence == null ? 'Pending' : `${data.confidence}%`;
    confidenceBar.style.width = data.confidence == null ? '0%' : `${data.confidence}%`;
    severity.textContent = data.severity || '—';
    zone.textContent = data.zone || '—';
    nextStep.textContent = data.next_step || '—';
  } catch (error) {
    resultTitle.textContent = 'Backend unavailable';
    resultText.textContent = `${error.message} Start the FastAPI server and try again.`;
    confidence.textContent = '—';
    confidenceBar.style.width = '0%';
    severity.textContent = '—';
    zone.textContent = '—';
    nextStep.textContent = 'Start API';
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
  });
});
