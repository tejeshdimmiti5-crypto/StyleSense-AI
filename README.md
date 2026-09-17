# 🌶️ ChilliProfit AI

**AI-Based Disease Detection and Profit Optimization for 1-Acre Chilli Farms**

ChilliProfit AI is a smart-farming project designed around the needs of small chilli farms in Andhra Pradesh and Telangana. The goal is to combine crop disease screening, farm-zone monitoring, irrigation intelligence, yield prediction and farm economics in one simple dashboard.

## Current version

The repository currently contains a responsive frontend prototype with:

- Chilli-focused landing page
- Leaf image upload and preview
- Disease-analysis result interface
- 1-acre 3×3 farm-zone map
- Zone risk indicators
- Basic revenue and net-return calculator
- Mobile-responsive design
- Clear separation between demo screening and future real ML inference

> **Important:** The disease result in the current frontend is a demo placeholder. It does not claim to diagnose a real plant disease. A trained computer-vision model must be connected before using the system for real agricultural decisions.

## Planned AI pipeline

```text
Leaf Image
   ↓
Image preprocessing
   ↓
Chilli disease model
   ↓
Disease + confidence + severity
   ↓
Farm zone mapping
   ↓
Risk / yield / economics engine
   ↓
Farmer dashboard
```

## Planned technology stack

- Frontend: HTML, CSS, JavaScript (prototype)
- Computer vision: CNN / transfer learning model
- Backend: Python + FastAPI
- ML: PyTorch or TensorFlow
- Database: PostgreSQL or MongoDB
- Weather: weather API
- Optional AI assistant: Gemini API through a server-side backend

API keys should **never** be committed to this repository. Use environment variables on the backend.

## Why chilli?

Andhra Pradesh reported about 246,752 hectares of dried chilli area and 1.44 million tonnes of production in its 2023–24 horticulture estimates. Telangana also identifies chilli as a major horticultural crop. These facts make chilli a useful regional focus for an AP/Telangana agriculture project, while farm income itself remains dependent on yield, costs, market prices, water and other conditions.

## Roadmap

- [ ] Collect and clean chilli disease dataset
- [ ] Train baseline disease classifier
- [ ] Compare lightweight models for mobile/edge deployment
- [ ] Add severity estimation
- [ ] Add real farm-zone records
- [ ] Add weather and soil inputs
- [ ] Add yield prediction
- [ ] Add cost/profit scenarios
- [ ] Add Telugu + English farmer interface
- [ ] Deploy secure backend

## Project name

**ChilliProfit AI — Smart 1-Acre Chilli Farming**
