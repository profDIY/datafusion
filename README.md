# ⬡ DataFusion · Sales Intelligence Suite
> Dark-themed Streamlit dashboard with login gate, CSV merge engine, and dynamic visual analytics.

---

## File Structure

```
datafusion/
├── app.py                        ← main Streamlit app (auth + dashboard)
├── run_once_generate_config.py   ← run once locally to create config.yaml
├── config.yaml                   ← generated credentials (DO NOT commit)
├── requirements.txt
├── .gitignore                    ← config.yaml is excluded
└── README.md
```

---

## Step 1 — Install dependencies

```bash
pip install -r requirements.txt
```

---

## Step 2 — Generate config.yaml (ONE TIME)

Edit `run_once_generate_config.py` to set your usernames, names, emails, and passwords.
Then run:

```bash
python run_once_generate_config.py
```

This creates `config.yaml` with bcrypt-hashed passwords. **Never commit this file.**

---

## Step 3 — Run locally

```bash
streamlit run app.py
```

Open http://localhost:8501 — you'll see the login screen first.

Default credentials (if you didn't change them):
| Username | Password     |
|----------|--------------|
| admin    | Admin1234!   |
| analyst  | Analyst1234! |

---

## Deploy to Streamlit Community Cloud (FREE)

### A. Push code to GitHub (without config.yaml)

```bash
git init
git add app.py requirements.txt run_once_generate_config.py README.md .gitignore
git commit -m "initial deploy"
git remote add origin https://github.com/YOUR_USERNAME/datafusion.git
git push -u origin main
```

### B. Add secrets on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
2. Connect your GitHub repo, set main file to `app.py`
3. Click **Advanced settings → Secrets**
4. Paste the contents of your local `config.yaml` converted to TOML format:

```toml
[credentials.usernames.admin]
name     = "Admin User"
email    = "admin@datafusion.io"
password = "$2b$12$PASTE_YOUR_BCRYPT_HASH_HERE"

[credentials.usernames.analyst]
name     = "Data Analyst"
email    = "analyst@datafusion.io"
password = "$2b$12$PASTE_YOUR_BCRYPT_HASH_HERE"

[cookie]
expiry_days = 7
key         = "datafusion_super_secret_key_CHANGE_ME"
name        = "datafusion_auth_cookie"
```

> Get the bcrypt hashes from your generated `config.yaml` — they look like `$2b$12$...`

### C. Load secrets in app.py (for Cloud deployment)

Replace the config file loading block at the top of `app.py` with:

```python
import streamlit as st
import yaml

# Works locally (reads config.yaml) and on Streamlit Cloud (reads st.secrets)
try:
    with open("config.yaml") as f:
        import yaml
        config = yaml.safe_load(f)
except FileNotFoundError:
    # Streamlit Cloud: secrets are injected via st.secrets
    config = {
        "credentials": dict(st.secrets["credentials"]),
        "cookie": dict(st.secrets["cookie"]),
    }
```

### D. Deploy

Click **Deploy** — live in ~90 seconds at `https://your-app.streamlit.app`.

---

## Deploy to Render (always-on, free tier)

1. Create a new **Web Service** on [render.com](https://render.com)
2. Connect your GitHub repo
3. Set:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
4. Add environment variables for secrets, or upload `config.yaml` via the Shell tab

---

## Deploy to Railway

```bash
railway login
railway init
railway up
```

Set start command to:
```
streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
```

---

## Adding / Removing Users

Edit `run_once_generate_config.py`, add/remove entries in `USERS`, re-run it, and redeploy.

---

## Security Notes

- `config.yaml` is in `.gitignore` — never commit it
- Change the `cookie.key` to a long random string (e.g. `openssl rand -hex 32`)
- Use strong passwords (12+ chars, mixed case + numbers + symbols)
- On Streamlit Cloud, always use Secrets — never hardcode credentials in `app.py`
