# 🌶️ ChilliProfit AI

**AI-Based Chilli Disease Detection and Farm Intelligence Platform**

ChilliProfit AI is a smart-farming platform designed to help chilli growers monitor crop health, identify possible diseases from leaf images, understand farm-zone risk and evaluate farm economics.

The platform is **not limited to a fixed farm size**. Farm zones, crop observations and economic inputs are designed to scale according to the user's actual farm.

## Current version

The repository currently contains a responsive frontend prototype with:

- Chilli-focused landing page
- Leaf image upload and preview
- Disease-analysis result interface
- Scalable farm-zone health map
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

## Core features planned

- AI chilli disease detection
- Disease severity estimation
- Farm-zone risk monitoring
- Weather-based crop risk insights
- Soil and irrigation intelligence
- Yield prediction
- Cost and profit scenarios
- Telugu + English farmer interface
- Secure backend API
- Historical crop-health records

## Roadmap

- [ ] Collect and clean chilli disease dataset
- [ ] Train baseline disease classifier
- [ ] Compare lightweight models for edge/mobile deployment
- [ ] Add severity estimation
- [ ] Replace demo farm zones with user-defined farm layouts
- [ ] Add weather and soil inputs
- [ ] Add yield prediction
- [ ] Add cost/profit scenarios
- [ ] Add Telugu + English farmer interface
- [ ] Deploy secure backend

## Project name

**ChilliProfit AI — Smart Chilli Farming Intelligence**
