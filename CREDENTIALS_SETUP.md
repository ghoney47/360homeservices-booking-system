# Getting the Service Account Key (JSON download was blocked)

**Project:** 360-schedule (`schedule-497019`)  
**Service account:** `sheets-access@schedule-497019.iam.gserviceaccount.com`  
**Target sheet:** Gavin's Schedule (`1fiT_JuS_oiETo9J0M7X3_SsiqZrlpwBiYDPVd6eYHpA`)

---

## Why the download was blocked

Google Workspace organisations can enforce an org policy called
`constraints/iam.disableServiceAccountKeyCreation` that blocks key downloads
**in the Cloud Console UI only**. The `gcloud` CLI and the IAM REST API are
often still allowed — try those first.

---

## Option 1 — gcloud CLI (most likely to work)

```bash
# Install gcloud if you haven't: https://cloud.google.com/sdk/docs/install

# Authenticate with your Google account
gcloud auth login

# Point at the right project
gcloud config set project schedule-497019

# Create and download the key
gcloud iam service-accounts keys create ~/keys/schedule-497019-sheets-access.json \
  --iam-account=sheets-access@schedule-497019.iam.gserviceaccount.com
```

If that succeeds, add to `backend/.env`:
```
GOOGLE_CREDENTIALS_PATH=/Users/ghoney/keys/schedule-497019-sheets-access.json
```

---

## Option 2 — Ask your Google Workspace admin

If the org policy blocks CLI key creation too, ask your admin to either:
- Temporarily lift `constraints/iam.disableServiceAccountKeyCreation` for
  project `schedule-497019`, OR
- Download the key themselves and send it via a secure channel (1Password,
  Google Drive encrypted share, etc.)

---

## Option 3 — Workload Identity (no JSON key at all)

If the app is deployed on **Google Cloud Run, GKE, or App Engine**, you can
attach the service account directly to the compute resource and skip JSON keys
entirely. `gspread` / `google-auth` will pick up credentials automatically via
the metadata server.

Steps:
1. Deploy the FastAPI backend to Cloud Run.
2. In the Cloud Run service settings → "Security" → set the service account to
   `sheets-access@schedule-497019.iam.gserviceaccount.com`.
3. Remove `GOOGLE_CREDENTIALS_PATH` / `GOOGLE_CREDENTIALS_JSON` from env vars
   entirely — `google-auth` detects Cloud Run automatically.

---

## After you have the key — share the Sheet

The service account must have **Editor** access to the spreadsheet:

1. Open **Gavin's Schedule**:
   https://docs.google.com/spreadsheets/d/1fiT_JuS_oiETo9J0M7X3_SsiqZrlpwBiYDPVd6eYHpA
2. Click **Share** (top-right).
3. Add `sheets-access@schedule-497019.iam.gserviceaccount.com` as an **Editor**.
4. Uncheck "Notify people" → **Share**.

---

## Quick smoke test

Once `.env` is filled in:

```bash
cd backend
pip install -r requirements.txt
python - <<'EOF'
from services.sheets_service import _get_worksheet
ws = _get_worksheet()
print("Connected! Worksheet:", ws.title)
print("Rows so far:", len(ws.get_all_records()))
EOF
```

You should see `Connected! Worksheet: Bookings` and a row count.
If you get a `RuntimeError` about credentials, the env var isn't set.
If you get a `gspread.exceptions.APIError: [403]`, the sheet hasn't been shared
with the service account yet.

---

## Sheet structure created automatically

On first booking the code creates a **"Bookings"** tab with these columns:

| A | B | C | D | E | F | G | H | I | J | K | L | M | N | O | P |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Booking ID | Client Name | Phone | Email | Street # | Street Name | City | State | Zip | Job Type | Date | Start Time | End Time | Price ($) | Status | Created At |
