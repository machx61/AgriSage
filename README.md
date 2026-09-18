# AgriSage

AgriSage is a Streamlit plant-disease diagnosis and plant-tracking application.

## Project structure

```text
.
├── app.py                 # Streamlit home page and diagnosis flow
├── pages/                 # Streamlit multipage views
├── agrisage/              # Reusable application code
│   ├── diagnosis_utils.py
│   ├── disease_map.py
│   ├── gemini_tracker.py
│   └── treatments_db.py
├── data/diseases/         # Crop treatment knowledge base
├── models/                # Local model weights
├── tests/                 # Automated tests
├── scripts/               # Manual model/API diagnostics
├── .streamlit/            # Local Streamlit configuration and secrets
└── requirements.txt
```

## Development

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

Run the automated tests:

```bash
python -m unittest discover -s tests -v
```

Set `GEMINI_API_KEY` in `.streamlit/secrets.toml` to enable Gemini-powered
diagnosis and plant progress analysis. The local SQLite history database is
created automatically at runtime and is intentionally not part of the source
layout.
