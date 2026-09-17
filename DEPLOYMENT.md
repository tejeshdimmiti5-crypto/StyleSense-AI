# ChilliProfit AI Deployment

## 1. Render API

The repository includes `render.yaml` and a Dockerfile. Create a Render Blueprint from this repository and deploy the `chilliprofit-ai-api` web service.

The Blueprint already contains:

- Docker runtime
- `/health` health check
- public `model-1` release URL
- SHA-256 verification for the trained model

After deployment, verify:

```text
GET https://<your-render-service>/health
GET https://<your-render-service>/api/health
```

`/api/health` should report `model_configured: true` and list the five model classes.

## 2. Connect the frontend

The frontend reads the backend URL from:

```js
window.CHILLIPROFIT_API_URL
```

Set it before `app.js` loads, for example:

```html
<script>
  window.CHILLIPROFIT_API_URL = 'https://<your-render-service>';
</script>
<script src="app.js"></script>
```

Then redeploy the static frontend through GitHub Pages or another static host.

## 3. CORS

Set the Render `FRONTEND_ORIGIN` environment variable to the exact deployed frontend origin, for example:

```text
https://<your-user>.github.io
```

For a custom domain, use that exact origin instead.

## 4. End-to-end check

Upload a JPG, PNG or WEBP chilli-leaf image from the frontend. The browser should call:

```text
POST /api/analyze
```

The response includes:

- predicted class
- model confidence
- class probabilities
- next-step guidance
- image metadata

The confidence value is a model-screening confidence measure, not biological disease severity.

## 5. Model updates

A push affecting `ml/**` or the training workflow automatically starts model training. Successful runs publish a new numbered GitHub Release. Update the model URL and SHA in `render.yaml` when promoting a new release to production.
