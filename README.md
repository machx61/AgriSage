# AgriSage

AgriSage is a Streamlit plant-disease diagnosis and plant-tracking application.

Leaf photos are diagnosed by Google Gemini, which is restricted to the classes
listed in `agrisage/disease_map.py`. Only crops with a treatment knowledge base
in `data/diseases/` are supported: **apple, brinjal, cabbage, capsicum, carrot, cauliflower, cucumber, garlic, maize (corn), mustard, okra, onion, pea, potato, rice, spinach, tomato
and wheat**. Photos of other crops are reported as unsupported.

## Project structure

```text
.
├── app.py                 # Streamlit home page and diagnosis flow
├── pages/                 # Streamlit multipage views
├── agrisage/              # Reusable application code
│   ├── auth.py            # Username/password accounts and login sessions
│   ├── db.py              # Accounts, scan history & plant tracking (Postgres or SQLite)
│   ├── diagnosis_utils.py
│   ├── disease_map.py     # Supported classes -> knowledge-base entries
│   ├── gemini_tracker.py  # Gemini diagnosis & progress analysis
│   ├── images.py
│   └── treatments_db.py
├── data/diseases/         # Crop treatment knowledge base
├── models/                # Experimental local weights (not used by the app)
├── tests/                 # Automated tests
├── scripts/               # list_models.py: list Gemini models for your key
│                          # keep_awake.py: visit the hosted app so it doesn't sleep
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

## Keeping the hosted app awake

Streamlit Community Cloud puts an app to sleep after 12 hours without visitors.
The `Keep app awake` GitHub Actions workflow opens the app in a browser every
4 hours and wakes it if needed. It visits https://agrisage.streamlit.app/ by
default; to point it elsewhere, set a repository variable named `APP_URL`
(Settings > Secrets and variables > Actions > Variables).

## Configuration

Set `GEMINI_API_KEY` in `.streamlit/secrets.toml` to enable Gemini-powered
diagnosis and plant progress analysis.

### Accounts and storage

Visitors can scan without an account; logging in (username + password) saves
scan history and tracked plants. Data lives in Postgres when `DATABASE_URL` is
set, otherwise in a local SQLite file (`agrisage_history.db`, git-ignored)
that is created automatically.

Streamlit Community Cloud wipes local files on restart, so the hosted app
needs Postgres. A free Supabase or Neon project works:

1. Create the project and copy its **pooled** connection string
   (Supabase: Project Settings > Database > Connection pooling;
   Neon: the host with `-pooler`). It looks like
   `postgresql://user:password@host:6543/postgres`.
2. Add it to the app's secrets (Streamlit Cloud: App settings > Secrets), and
   to `.streamlit/secrets.toml` only if you want local runs to use it too:

   ```toml
   DATABASE_URL = "postgresql://user:password@host:6543/postgres"
   ```

Tables are created on first run. The tests always use a temporary SQLite file.
