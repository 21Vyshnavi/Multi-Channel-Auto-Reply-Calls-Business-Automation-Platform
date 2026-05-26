# Streamlit Dashboard

Streamlit UI for the unified inbox API.

## Run
```bash
cd "/Users/vaish/Documents/New project"
python3 -m venv .venv
source .venv/bin/activate
pip install -r apps/streamlit/requirements.txt
npm run dev:api
streamlit run apps/streamlit/app.py
```

If you get connection errors, set the Streamlit sidebar **API base URL** to `http://127.0.0.1:8080` (some systems resolve `localhost` to IPv6 `::1`).
