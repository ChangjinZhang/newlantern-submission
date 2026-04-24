# New Lantern Relevant Priors API

This is a simple Flask API for the New Lantern challenge.

## Endpoint

`POST /predict`

## Local run

```bash
pip install -r requirements.txt
python app.py
```

Then test:

```bash
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

## Deploy on Render

1. Upload this folder to a GitHub repository.
2. Go to Render and create a new Web Service.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
5. After deployment, submit the URL: `https://your-service.onrender.com/predict`
