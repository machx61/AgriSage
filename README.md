# AgriSage

AgriSage is a Streamlit plant-disease diagnosis and plant-tracking application.

Leaf photos are diagnosed by Google Gemini, which is restricted to the classes
listed in `agrisage/disease_map.py`. Only crops with a treatment knowledge base
in `data/diseases/` are supported: **maize (corn), okra, potato, rice, tomato
and wheat**. Photos of other crops are reported as unsupported.

## Project structure

```text
.
├── app.py                 # Streamlit home page and diagnosis flow
├── pages/                 # Streamlit multipage views
├── agrisage/              # Reusable application code
│   ├── db.py              # SQLite scan history & plant tracking
│   ├── diagnosis_utils.py
│   ├── disease_map.py     # Supported classes -> knowledge-base entries
│   ├── gemini_tracker.py  # Gemini diagnosis & progress analysis
│   ├── images.py
│   ├── session.py         # Browser device ID
│   └── treatments_db.py
├── data/diseases/         # Crop treatment knowledge base
├── models/                # Experimental local weights (not used by the app)
├── tests/                 # Automated tests
├── scripts/               # list_models.py: list Gemini models for your key
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
