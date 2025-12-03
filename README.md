# FreshGuard API

Computer-vision powered API for assessing tomato freshness and providing actionable guidance for buyers and sellers. This service powers the Bolt.new UI at:

- Live app: https://freshguard-nigerian-f8qp.bolt.host/

The API exposes endpoints for health checks and image-based predictions, returning a freshness score, category, confidence, shelf-life guidance, market action, pricing guidance, urgency, and whether cooling is recommended. It also supports the UI flows for buyers (consumers) and sellers (farmers/businesses), including suggested storage hubs.


## Features

- Image classification using a pre-trained Keras model (keras_model.h5)
- Freshness categories: Ripe, Unripe, Old, Damaged
- Confidence-aware scoring logic with shelf-life and action recommendations
- CORS enabled for web frontends (e.g., Bolt.new)
- Designed to support buyer and seller workflows
- Future integration points for storage hubs (e.g., Ecotutu, Soilless Farm Lab) and inventory/traceability


## Architecture Overview

- Framework: Flask (Python)
- Model: Keras/TensorFlow model loaded from `keras_model.h5` with labels in `labels.txt`
- API layer: Flask routes in `app.py`
- Frontend: Implemented separately in Bolt.new and consumes this API
- Containerization: Dockerfile and docker-compose provided
- CI (optional): Docker build/push workflow under `.github/workflows/`


## Repository Contents

- `app.py` — Flask API server with prediction and scoring logic
- `keras_model.h5` — Pre-trained Keras model file
- `labels.txt` — Class labels aligned with model outputs
- `requirements.txt` — Python dependencies
- `Dockerfile` — Container image build definition
- `docker-compose.yml` — Local container orchestration
- `.env` — Environment variables (not strictly required by default app)
- `LICENSE` — Project license


## Setup and Local Development

Prerequisites:
- Python 3.9+
- pip
- (Optional) Docker & Docker Compose

### 1) Clone and install dependencies

```bash
pip install -r requirements.txt
```

### 2) Ensure model artifacts are present
- Confirm `keras_model.h5` and `labels.txt` exist in the repository root (same directory as `app.py`).

### 3) Run the API locally

```bash
python app.py
```

By default, the server binds to `0.0.0.0:5001`. You can adjust host/port in `app.py` as needed.

### 4) Test health endpoint

```bash
curl http://localhost:5001/health
# {"status":"healthy"}
```


## API Reference

Base URL (local): `http://localhost:5001`

- Health Check
  - Method: GET
  - Path: `/health`
  - Response: `{ "status": "healthy" }`

- Predict Freshness
  - Method: POST
  - Path: `/predict`
  - Content-Type: `multipart/form-data`
  - Form field: `image` (file: png, jpg, jpeg, gif)
  - Response example:
    ```json
    {
      "score": 95,
      "category": "Ripe",
      "confidence": 98.73,
      "shelf_life": "5-7 days",
      "action": "Premium market ready - excellent for immediate sale",
      "pricing": "Full market price (₦15,000-₦18,000/basket)",
      "urgency": "low",
      "cooling_needed": false
    }
    ```

Notes:
- `category` is derived from the model label.
- `score` is adjusted by confidence bands to reflect prediction certainty.
- When confidence falls below 70%, the `action` field includes a cautionary note to double-check visually.


## Frontend Flows (Bolt.new)

The UI provides two entry points:
- "I'm buying for consumers" (buyers)
- "I'm selling" (sellers: farmers and business operators)

Both flows allow scanning tomatoes (via image upload/capture) and consume the `/predict` endpoint for freshness insights. The UI also suggests storage hubs such as Ecotutu and Soilless Farm Lab, with quick actions:
- Directions: deep links to Google Maps for navigation
- Phone numbers: click-to-call for rapid contact


## Roadmap (Phase 2+)

- Seller inventory and batch management
- Deeper synchronization with storage facilities
- Traceability systems (lot IDs, farm-to-market provenance)
- Expanded produce coverage and classes
- Model improvement loop with active learning and human-in-the-loop verification
- Role-based access (buyers vs sellers) and analytics dashboards


## Deployment

### Docker (local)

Build image:
```bash
docker build -t freshguard-api .
```

Run container:
```bash
docker run --rm -p 5001:5001 freshguard-api
```

### Docker Compose

```bash
docker-compose up --build
```

The service will be available at `http://localhost:5001`.

### Environment Variables

The service runs with sensible defaults and does not require environment variables by default. If you introduce configuration (e.g., model path, logging level), add them to `.env` and load using your preferred method.


## Production Considerations

- Set `debug=False` (already configured) and run behind a production WSGI server (e.g., gunicorn) when containerizing
- Configure request size limits and basic auth/API keys if exposing publicly
- Validate/clean inputs and add rate limiting when necessary
- Centralized logging and monitoring for model performance
- Model versioning and A/B testing for safe upgrades


## Development Tips

- Accepted file types: png, jpg, jpeg, gif
- Ensure uploaded images are RGB-convertible; corrupted files return a 400/500 error
- The classification index is resolved using `labels.txt` with `[index] label` convention; the code trims the index prefix
- Modify `get_freshness_details` in `app.py` to tune scores, messages, and pricing bands


## Example Client Snippet

Python example using `requests`:

```python
import requests

url = "http://localhost:5001/predict"
files = {"image": open("sample.jpg", "rb")}
resp = requests.post(url, files=files)
print(resp.json())
```

JavaScript (browser) using Fetch:

```js
const form = new FormData();
form.append("image", fileInput.files[0]);

fetch("http://localhost:5001/predict", {
  method: "POST",
  body: form,
})
  .then((r) => r.json())
  .then(console.log)
  .catch(console.error);
```


## License

This project is licensed under the terms of the LICENSE file included in this repository.
