# Oral Disease Classification FastAPI Deployment

Production-ready FastAPI service for the existing trained Oral Disease Classification model saved as `best_model.keras`.

The service does not retrain, rebuild, convert, or modify the model. It loads the existing native Keras model from the project root and applies the same inference preprocessing used in the notebook:

- RGB image loading
- Resize to `224 x 224`
- No pixel rescaling or normalization
- Batch dimension added before prediction
- Softmax argmax class selection
- Max probability confidence calculation

## Folder Structure

```text
fastapi_deployment/
|-- app.py
|-- predict.py
|-- model_loader.py
|-- preprocessing.py
|-- config.py
|-- schemas.py
|-- utils.py
|-- classes.json
|-- requirements.txt
|-- README.md
|-- .gitignore
|-- uploads/
|-- responses/
|-- models/
`-- logs/
```

## Installation

From the deployment folder:

```bash
cd fastapi_deployment
python -m venv .venv
```

Activate the virtual environment.

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

Start the API from `fastapi_deployment`:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

The application loads `../best_model.keras` during startup and fails with a clear error if the model or `classes.json` is missing.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/` | API metadata |
| GET | `/health` | Startup/model/class validation status |
| POST | `/predict` | Upload an oral image and return model prediction |

## Documentation

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

## Example Request

```bash
curl -X POST "http://localhost:8000/predict" ^
  -F "file=@sample.jpg"
```

Linux/macOS:

```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@sample.jpg"
```

## Example Response

```json
{
  "predicted_class": "Gingivitis",
  "confidence": 98.45,
  "all_predictions": {
    "Calculus": 0.1023,
    "Data caries": 0.2214,
    "Gingivitis": 98.45,
    "Mouth Ulcer": 0.3412,
    "Tooth Discoloration_": 0.5133,
    "hypodontia": 0.2201,
    "normal": 0.1517
  }
}
```

## Compatibility Notes

The notebook metadata reports Python `3.12.13`. The native Keras archive metadata reports Keras `3.13.2`. The requirements pin Keras to that saved-model version and TensorFlow to a compatible modern release that supports Python 3.12 and the `.keras` model format.
