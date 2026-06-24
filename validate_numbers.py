"""
validate_numbers.py — Pre-validate WhatsApp numbers BEFORE bulk send.
=====================================================================
Checks every number in your CSV against WhatsApp via Gallabox.
Splits your list into two clean files:

    data/valid_numbers.csv    ← on WhatsApp — safe to send
    data/invalid_numbers.csv  ← not on WhatsApp — skip these

ALWAYS run this before main_pipeline.py to avoid 131026 errors.

Usage:
    python validate_numbers.py                         # full list
    python validate_numbers.py --csv data/custom.csv   # custom file
    python validate_numbers.py --limit 200             # first 200 only
    python validate_numbers.py --delay 0.5             # 0.5s between checks
    After this completes, run:
    python main_pipeline.py
"""

import os
import time
import argparse
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

GALLABOX_API_KEY    = os.getenv("GALLABOX_API_KEY")
GALLABOX_API_SECRET = os.getenv("GALLABOX_API_SECRET")
CHANNEL_ID          = os.getenv("CHANNEL_ID")

VALIDATE_URL = "https://server.gallabox.com/devapi/contacts/check"

COL_NAME   = "Cust_Name"
COL_MOON   = "Moon_sign"
COL_NAK    = "Nakshatra"
COL_MOBILE = "Mobile_Number"
VALID_OUT   = "data/valid_numbers.csv"
INVALID_OUT = "data/invalid_numbers.csv"


def clean_mobile(mobile: str) -> str | None:
    """Normalise to 91XXXXXXXXXX. Returns None if invalid."""
    mobile = str(mobile).strip().replace(" ", "").replace("-", "")
    if mobile.startswith("+91"):
        mobile = mobile[3:]
    elif mobile.startswith("91") and len(mobile) == 12:
        mobile = mobile[2:]
    if len(mobile) != 10 or not mobile.isdigit():
        return None
    return "91" + mobile


def check_whatsapp(mobile: str, retries: int = 2) -> bool:
    """
    Returns True if the number is registered on WhatsApp.
    Retries up to 2 times on network errors or rate limits.
    """
    headers = {
        "apiKey":       GALLABOX_API_KEY,
        "apiSecret":    GALLABOX_API_SECRET,
        "Content-Type": "application/json",
    }
    payload = {
        "channelId":   CHANNEL_ID,
        "channelType": "whatsapp",
        "phone":       mobile,
    }

    for attempt in range(retries + 1):
        try:
            r = requests.post(VALIDATE_URL, json=payload,
                              headers=headers, timeout=10)

            if r.status_code == 429:
                print(f"    ⚠️  Rate limited — waiting 30s...")
                time.sleep(30)
                continue

            if r.status_code in [200, 202]:
                data = r.json()
                return bool(
                    data.get("exists")
                    or data.get("isValid")
                    or str(data.get("status", "")).lower()
                    in ["valid", "exists", "active"]
                )
            return False

        except requests.exceptions.Timeout:
            if attempt < retries:
                time.sleep(2)
            continue
        except Exception:
            return False

    return False


def main():
    parser = argparse.ArgumentParser(
        description="Pre-validate WhatsApp numbers — AstroVed"
    )
    parser.add_argument("--csv",   default="data/customer_data.csv")
    parser.add_argument("--limit", type=int,   default=None)
    parser.add_argument("--delay", type=float, default=0.3)
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  WhatsApp Number Validator")
    print(f"  Input   : {args.csv}")
    print(f"  Valid   → {VALID_OUT}")
    print(f"  Invalid → {INVALID_OUT}")
    print(f"{'='*60}\n")

    df = pd.read_csv(args.csv, dtype=str, on_bad_lines='skip', quoting=3, engine='python').fillna("")
    df.columns = df.columns.str.strip()

    if args.limit: 
        df = df.head(args.limit)
        print(f"  [LIMIT] Checking first {args.limit} rows\n")

    total   = len(df)
    valid   = []
    invalid = []

    print(f"  Checking {total} numbers...\n")

    for idx, row in df.iterrows():
        name   = str(row.get(COL_NAME,   "")).strip()
        mobile = str(row.get(COL_MOBILE, "")).strip()
        cleaned = clean_mobile(mobile)

        label = f"[{idx+1}/{total}]  {name:<20}  {mobile}"

        if not cleaned:
            print(f"  {label}  →  ❌ INVALID FORMAT")
            invalid.append(row)
            continue

        on_wa = check_whatsapp(cleaned)

        if on_wa:
            print(f"  {label}  →  ✅ ON WHATSAPP")
            valid.append(row)
        else:
            print(f"  {label}  →  ❌ NOT ON WHATSAPP")
            invalid.append(row)

        if (idx + 1) < total:
            time.sleep(args.delay)

    # ── Save ──────────────────────────────────────────────────────────────────
    os.makedirs("data", exist_ok=True)
    pd.DataFrame(valid).to_csv(VALID_OUT,   index=False)
    pd.DataFrame(invalid).to_csv(INVALID_OUT, index=False)

    pct = round(len(valid) / total * 100, 1) if total else 0

    print(f"\n{'='*60}")
    print(f"  VALIDATION COMPLETE")
    print(f"  Total     : {total}")
    print(f"  ✅ Valid   : {len(valid)}  ({pct}%)  → {VALID_OUT}")
    print(f"  ❌ Invalid : {len(invalid)}           → {INVALID_OUT}")
    print(f"\n  ▶  Next step:")
    print(f"     python main_pipeline.py")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()