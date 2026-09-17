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

leafInput.addEventListener('change', () => {
  const file = leafInput.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = event => {
    preview.src = event.target.result;
    preview.hidden = false;
    uploadContent.hidden = true;
    runDemoAnalysis();
  };
  reader.readAsDataURL(file);
});

function runDemoAnalysis() {
  // Demo-only result. Replace this function with the real ML/API response.
  const demo = {
    title: 'Possible leaf disease',
    text: 'The image has been accepted for screening. Connect the trained chilli model to return a real disease class.',
    confidence: 92,
    severity: 'Moderate',
    zone: 'Zone 5',
    next: 'Inspect nearby plants'
  };
  resultTitle.textContent = demo.title;
  resultText.textContent = demo.text;
  confidence.textContent = `${demo.confidence}%`;
  confidenceBar.style.width = `${demo.confidence}%`;
  severity.textContent = demo.severity;
  zone.textContent = demo.zone;
  nextStep.textContent = demo.next;
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
