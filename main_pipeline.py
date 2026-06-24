"""
main_pipeline.py — AstroVed Bulk WhatsApp Sender (Phase-by-Phase)
=================================================================
READS DIRECTLY FROM: data/customer_data.csv  (no validate_numbers.py needed)
Sends to ALL users with no number restriction — Gallabox handles delivery.

131049 STRATEGY — "Healthy Ecosystem Engagement" error:
  Meta triggers 131049 when it detects bulk-like sending patterns.
  Three rules keep you clean:
    1. WARM-UP RAMP   — first 20 messages use a 20s delay (slower start)
    2. RANDOM JITTER  — every delay has ±3s randomness (not robotic)
    3. HOURLY PAUSE   — after every 50 sends, pause 3 minutes
  These mimic natural human send patterns and avoid Meta rate detection.

WEEKLY PHASE PLAN (default 500 users/week):
  Week 1  → users    1 –  500   (rows 0–499)
  Week 2  → users  501 – 1000   (rows 500–999)
  ...and so on until all users are covered.

USAGE:
  python main_pipeline.py --week 1                  # Send to users 1–500
  python main_pipeline.py --week 2                  # Send to users 501–1000
  python main_pipeline.py --week 1 --preview        # Dry run — no messages sent
  python main_pipeline.py --week 1 --delay 15       # Custom delay (default 12s)
  python main_pipeline.py --status                  # Show progress of all weeks
  python main_pipeline.py --week 1 --batch-size 250 # Smaller batch

OUTPUT FILES:
  data/sent_numbers.csv   — tracks delivered numbers (dedup — never cleared)
  data/failed_numbers.csv — CLEARED and recreated fresh on every run start
  data/sending_log.csv    — full per-attempt log for every send this run

PRE-REQUISITES:
  1. python db_conn.py                 <- Pull latest customers from DB
  2. python test_send.py               <- Test with 1-2 real numbers first
  3. python main_pipeline.py --week 1  <- Start sending Week 1
"""

import os
import time
import random
import argparse
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from whatsapp.template_sender import send_template

load_dotenv()

# ── File paths ────────────────────────────────────────────────────────────────
INPUT_CSV   = "data/customer_data.csv"
SENT_CSV    = "data/sent_numbers.csv"
FAILED_CSV  = "data/failed_numbers.csv"
SENDING_LOG = "data/sending_log.csv"

# ── Column names — must match db_conn.py output exactly ──────────────────────
COL_NAME   = "Cust_Name"
COL_MOON   = "Moon_sign"
COL_NAK    = "Nakshatra"
COL_MOBILE = "Mobile_Number"

# ── Phase settings ────────────────────────────────────────────────────────────
BATCH_SIZE    = 500
DEFAULT_DELAY = 12.0   # seconds between sends (normal pace)
MIN_DELAY     = 10.0   # absolute floor — never go below this
WARMUP_DELAY  = 20.0   # first WARMUP_COUNT messages use this slower delay
WARMUP_COUNT  = 20     # number of warm-up messages at run start
JITTER_SECS   = 3.0    # +/- random jitter on every delay
HOURLY_BATCH  = 50     # pause after every N sends
HOURLY_PAUSE  = 180    # seconds to pause between hourly batches (3 min)

# ── Time window (IST) ─────────────────────────────────────────────────────────
SEND_HOUR_START = 8
SEND_HOUR_END   = 21

# ── 131049 circuit breaker ────────────────────────────────────────────────────
CIRCUIT_BREAKER_THRESHOLD = 0.20
CIRCUIT_BREAKER_PAUSE     = 1800   # 30 min

# ── Log column headers ────────────────────────────────────────────────────────
SENDING_LOG_COLUMNS = [
    "timestamp", "week", "row_num", "Cust_Id",
    COL_NAME, COL_MOON, COL_NAK, COL_MOBILE,
    "status", "error_code", "var1", "var2", "var3",
]
FAILED_LOG_COLUMNS = [
    "Cust_Id", COL_NAME, COL_MOON, COL_NAK, COL_MOBILE,
    "error_code", "failed_at",
]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _normalise_mobile(mobile: str) -> str:
    m = str(mobile).strip().replace(" ", "").replace("-", "")
    if m.startswith("+91"):
        m = m[3:]
    elif m.startswith("91") and len(m) == 12:
        m = m[2:]
    return "91" + m[-10:] if len(m) >= 10 else m


def _jittered_delay(base: float) -> float:
    """Add random +/- jitter so sends never look robotic to Meta."""
    jitter = random.uniform(-JITTER_SECS, JITTER_SECS)
    return max(MIN_DELAY, base + jitter)


def _check_send_window(preview: bool = False) -> None:
    now_hour = datetime.now().hour
    if SEND_HOUR_START <= now_hour < SEND_HOUR_END:
        return
    if preview:
        print(f"  WARNING: Outside safe send window "
              f"({SEND_HOUR_START}:00-{SEND_HOUR_END}:00 IST). Preview only.\n")
        return
    print(f"\n  SEND BLOCKED - Current hour ({now_hour}:xx IST) outside safe window.")
    print(f"  Re-run between {SEND_HOUR_START}:00 and {SEND_HOUR_END}:00 IST.\n")
    raise SystemExit(1)


# ─────────────────────────────────────────────────────────────────────────────
# File init — clears failed_numbers.csv and sending_log.csv on every run
# sent_numbers.csv is NEVER cleared (it is the permanent dedup guard)
# ─────────────────────────────────────────────────────────────────────────────

def init_run_files(week: int, preview: bool = False) -> None:
    os.makedirs("data", exist_ok=True)
    if preview:
        return
    pd.DataFrame(columns=FAILED_LOG_COLUMNS).to_csv(
        FAILED_CSV, mode="w", header=True, index=False
    )
    pd.DataFrame(columns=SENDING_LOG_COLUMNS).to_csv(
        SENDING_LOG, mode="w", header=True, index=False
    )
    print(f"  [INIT] failed_numbers.csv — cleared, fresh start for week {week}.")
    print(f"  [INIT] sending_log.csv    — cleared, logging this run from scratch.\n")


# ─────────────────────────────────────────────────────────────────────────────
# Sent log (permanent — never wiped)
# ─────────────────────────────────────────────────────────────────────────────

def load_sent_numbers() -> set:
    if not os.path.exists(SENT_CSV):
        return set()
    df = pd.read_csv(SENT_CSV, dtype=str, encoding="utf-8-sig")
    return set(df[COL_MOBILE].astype(str).str.strip())


def save_sent_number(mobile: str, row: dict = None) -> None:
    key = _normalise_mobile(mobile)
    record = {
        "Cust_Id":  row.get("Cust_Id", "") if row else "",
        COL_NAME:   row.get(COL_NAME,  "") if row else "",
        COL_MOON:   row.get(COL_MOON,  "") if row else "",
        COL_NAK:    row.get(COL_NAK,   "") if row else "",
        COL_MOBILE: key,
        "sent_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    df_new    = pd.DataFrame([record])
    write_hdr = not os.path.exists(SENT_CSV)
    df_new.to_csv(SENT_CSV, mode="a", header=write_hdr, index=False)


# ─────────────────────────────────────────────────────────────────────────────
# Failed log (cleared each run by init_run_files)
# ─────────────────────────────────────────────────────────────────────────────

def save_failed(row: dict, error_code: str) -> None:
    record = {
        "Cust_Id":    row.get("Cust_Id", ""),
        COL_NAME:     row.get(COL_NAME,  ""),
        COL_MOON:     row.get(COL_MOON,  ""),
        COL_NAK:      row.get(COL_NAK,   ""),
        COL_MOBILE:   row.get(COL_MOBILE,""),
        "error_code": error_code,
        "failed_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    pd.DataFrame([record]).to_csv(FAILED_CSV, mode="a", header=False, index=False)


# ─────────────────────────────────────────────────────────────────────────────
# Sending log — every attempt logged here (cleared each run)
# ─────────────────────────────────────────────────────────────────────────────

def log_send_attempt(
    week: int, row_num: int, row: dict,
    status: str, error_code: str = "",
    var1: str = "", var2: str = "", var3: str = "",
) -> None:
    record = {
        "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "week":       week,
        "row_num":    row_num,
        "Cust_Id":    row.get("Cust_Id",  ""),
        COL_NAME:     row.get(COL_NAME,   ""),
        COL_MOON:     row.get(COL_MOON,   ""),
        COL_NAK:      row.get(COL_NAK,    ""),
        COL_MOBILE:   row.get(COL_MOBILE, ""),
        "status":     status,
        "error_code": error_code,
        "var1":       var1,
        "var2":       var2,
        "var3":       var3,
    }
    pd.DataFrame([record]).to_csv(SENDING_LOG, mode="a", header=False, index=False)


# ─────────────────────────────────────────────────────────────────────────────
# Misc utils
# ─────────────────────────────────────────────────────────────────────────────

def get_week_range(week_number: int, batch_size: int = BATCH_SIZE) -> tuple:
    start = (week_number - 1) * batch_size
    end   = start + batch_size - 1
    return start, end


def _eta(remaining: int, delay: float) -> str:
    total_secs = remaining * delay
    hours = int(total_secs // 3600)
    mins  = int((total_secs % 3600) // 60)
    if hours > 0:
        return f"~{hours}h {mins}m left"
    return f"~{mins}m left"


# ─────────────────────────────────────────────────────────────────────────────
# STATUS command
# ─────────────────────────────────────────────────────────────────────────────

def show_status() -> None:
    print(f"\n{'='*65}")
    print(f"  WEEKLY PHASE STATUS - AstroVed")
    print(f"{'='*65}")

    if not os.path.exists(INPUT_CSV):
        print(f"\n  ERROR: {INPUT_CSV} not found. Run: python db_conn.py first.\n")
        return

    df = pd.read_csv(INPUT_CSV, dtype=str, encoding="utf-8-sig",
                     on_bad_lines="skip", engine="python").fillna("")
    df.columns = df.columns.str.strip()
    total_rows = len(df)

    sent_numbers = load_sent_numbers()
    total_sent   = len(sent_numbers)
    total_weeks  = (total_rows + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"\n  Source CSV         : {INPUT_CSV}")
    print(f"  Total users        : {total_rows}")
    print(f"  Sent so far        : {total_sent}")
    print(f"  Remaining          : {total_rows - total_sent}")
    print(f"  Batch size         : {BATCH_SIZE} users per week")
    print(f"  Total weeks needed : {total_weeks}")
    print(f"  Safe send window   : {SEND_HOUR_START}:00 - {SEND_HOUR_END}:00 IST")
    print()
    print(f"  {'Week':<8} {'User Range':<20} {'Batch':<8} Status")
    print(f"  {'-'*55}")

    for week in range(1, total_weeks + 1):
        start_idx, end_idx = get_week_range(week)
        end_idx  = min(end_idx, total_rows - 1)
        batch_df = df.iloc[start_idx : end_idx + 1]

        batch_sent = sum(
            1 for _, row in batch_df.iterrows()
            if _normalise_mobile(str(row.get(COL_MOBILE, ""))) in sent_numbers
        )
        batch_total = len(batch_df)
        user_start  = start_idx + 1
        user_end    = end_idx + 1

        if batch_sent == 0:
            status = "PENDING"
        elif batch_sent >= batch_total:
            status = "DONE"
        else:
            status = f"PARTIAL  ({batch_sent}/{batch_total} sent)"

        print(f"  Week {week:<4} {user_start:>5} - {user_end:<10}  {batch_total:<8} {status}")

    if os.path.exists(SENDING_LOG):
        try:
            log_df = pd.read_csv(SENDING_LOG, dtype=str, encoding="utf-8-sig")
            if not log_df.empty and "status" in log_df.columns:
                counts = log_df["status"].value_counts().to_dict()
                print(f"\n  Last run sending_log.csv summary:")
                for s, c in counts.items():
                    print(f"    {s:<15} : {c}")
        except Exception:
            pass

    print(f"\n{'='*65}\n")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN SEND LOOP
# ─────────────────────────────────────────────────────────────────────────────

def run_week(week_number: int, preview: bool = False, delay: float = DEFAULT_DELAY) -> None:

    if delay < MIN_DELAY and not preview:
        print(f"\n  WARNING: Delay {delay}s below safe minimum {MIN_DELAY}s. Auto-correcting.\n")
        delay = MIN_DELAY

    _check_send_window(preview=preview)

    if not os.path.exists(INPUT_CSV):
        print(f"\n  ERROR: {INPUT_CSV} not found. Run: python db_conn.py first.\n")
        return

    init_run_files(week_number, preview=preview)

    df = pd.read_csv(INPUT_CSV, dtype=str, encoding="utf-8-sig",
                     on_bad_lines="skip", engine="python").fillna("")
    df.columns = df.columns.str.strip()
    total_rows = len(df)

    start_idx, end_idx = get_week_range(week_number)

    if start_idx >= total_rows:
        max_week = (total_rows + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"\n  ERROR: Week {week_number} out of range. Max week is {max_week}.\n")
        return

    end_idx           = min(end_idx, total_rows - 1)
    batch_df          = df.iloc[start_idx : end_idx + 1].reset_index(drop=True)
    batch_size_actual = len(batch_df)
    user_start        = start_idx + 1
    user_end          = end_idx + 1

    sent_numbers = load_sent_numbers()

    mode_label = "PREVIEW MODE - no messages sent" if preview else "LIVE SEND"
    print(f"\n{'='*65}")
    print(f"  WEEK {week_number} - {mode_label}")
    print(f"  Source       : {INPUT_CSV}  ({total_rows} total users)")
    print(f"  User range   : {user_start} to {user_end}  ({batch_size_actual} this week)")
    print(f"  Base delay   : {delay}s  (+/- {JITTER_SECS}s jitter)")
    print(f"  Warm-up      : first {WARMUP_COUNT} msgs at {WARMUP_DELAY}s delay")
    print(f"  Hourly pause : {HOURLY_PAUSE}s every {HOURLY_BATCH} sends")
    if not preview:
        print(f"  Est. time    : {_eta(batch_size_actual, delay)}")
    print(f"{'='*65}\n")

    delivered       = 0
    failed          = 0
    skipped         = 0
    error_131049    = 0
    sends_this_hour = 0

    for i, row in batch_df.iterrows():
        name      = str(row.get(COL_NAME,   "")).strip()
        moon      = str(row.get(COL_MOON,   "")).strip()
        nakshatra = str(row.get(COL_NAK,    "")).strip()
        mobile    = str(row.get(COL_MOBILE, "")).strip()

        row_num  = start_idx + i + 1
        row_dict = dict(row)

        # ── Already sent ──────────────────────────────────────────────────────
        key = _normalise_mobile(mobile)
        if key in sent_numbers:
            print(f"  [{row_num}] SKIP (already sent) : {name}  ({mobile})")
            skipped += 1
            log_send_attempt(
                week=week_number, row_num=row_num, row=row_dict,
                status="skipped", error_code="already_sent",
            )
            continue

        # ── Missing data ──────────────────────────────────────────────────────
        if not name or not mobile:
            print(f"  [{row_num}] SKIP (missing data) : name='{name}' mobile='{mobile}'")
            skipped += 1
            log_send_attempt(
                week=week_number, row_num=row_num, row=row_dict,
                status="skipped", error_code="missing_data",
            )
            continue

        # ── PREVIEW ───────────────────────────────────────────────────────────
        if preview:
            print(f"  [{row_num}] PREVIEW  {name:<22} "
                  f"{moon.title():<14} {nakshatra.title():<22} {mobile}")
            delivered += 1
            continue

        # ── Mid-batch time window check ───────────────────────────────────────
        if not (SEND_HOUR_START <= datetime.now().hour < SEND_HOUR_END):
            print(f"\n  Reached {SEND_HOUR_END}:00 IST - pausing. Resume tomorrow.")
            print(f"  Progress saved. Re-run --week {week_number} to continue.\n")
            break

        sends_done = delivered + failed
        sends_left = batch_size_actual - skipped - sends_done - 1
        print(f"  [{row_num}/{user_end}]  {name}  |  "
              f"{moon.title()} Moon  |  {nakshatra.title()}  |  {mobile}"
              f"  |  {_eta(sends_left, delay)}")

        # ── Send ──────────────────────────────────────────────────────────────
        success, error_code = send_template(
            name=name,
            moon=moon,
            nakshatra=nakshatra,
            mobile=mobile,
        )

        log_var1 = f"{name.split()[0]} | {moon.title()} Moon | {nakshatra.title()} Nakshatra"

        if success:
            delivered       += 1
            sends_this_hour += 1
            save_sent_number(mobile, row=row_dict)
            log_send_attempt(
                week=week_number, row_num=row_num, row=row_dict,
                status="delivered", var1=log_var1,
            )
            print(f"  Delivered  (session total: {delivered})\n")
        else:
            failed += 1
            save_failed(row_dict, str(error_code))
            log_send_attempt(
                week=week_number, row_num=row_num, row=row_dict,
                status="failed", error_code=str(error_code), var1=log_var1,
            )
            print(f"  FAILED - error: {error_code}\n")
            if error_code and "131049" in str(error_code):
                error_131049 += 1

        # ── Circuit breaker ───────────────────────────────────────────────────
        processed = delivered + failed
        if processed >= 10:
            if (error_131049 / processed) >= CIRCUIT_BREAKER_THRESHOLD:
                pause_mins = CIRCUIT_BREAKER_PAUSE // 60
                print(f"\n  CIRCUIT BREAKER: {error_131049}/{processed} hits on 131049.")
                print(f"  Pausing {pause_mins} min — Meta rate window resets. Progress saved.\n")
                time.sleep(CIRCUIT_BREAKER_PAUSE)
                error_131049 = 0

        # ── Hourly micro-pause ────────────────────────────────────────────────
        if sends_this_hour > 0 and sends_this_hour % HOURLY_BATCH == 0:
            pause_mins = HOURLY_PAUSE // 60
            print(f"\n  Hourly pause after {HOURLY_BATCH} sends — waiting {pause_mins} min "
                  f"to stay under Meta engagement limit...\n")
            time.sleep(HOURLY_PAUSE)

        # ── Delay before next send ────────────────────────────────────────────
        if i < batch_size_actual - 1:
            actual_sends = delivered + failed
            if actual_sends <= WARMUP_COUNT:
                sleep_for = _jittered_delay(WARMUP_DELAY)
                print(f"  [WARMUP {actual_sends}/{WARMUP_COUNT}] Sleeping {sleep_for:.1f}s...")
            else:
                sleep_for = _jittered_delay(delay)
            time.sleep(sleep_for)

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*65}")
    print(f"  WEEK {week_number} COMPLETE — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*65}")
    print(f"  Users in batch : {batch_size_actual}")

    if preview:
        print(f"  (Preview only — nothing sent)")
    else:
        print(f"  Delivered      : {delivered}")
        print(f"  Failed         : {failed}")
        print(f"  Skipped        : {skipped}")
        print(f"  131049 hits    : {error_131049}")

        total_sent_now = len(load_sent_numbers())
        remaining      = total_rows - total_sent_now
        print(f"\n  Total sent (all weeks) : {total_sent_now}")
        print(f"  Remaining              : {remaining}")

        if failed > 0:
            print(f"\n  Failed numbers saved to : {FAILED_CSV}")
            print(f"  Retry after 24 hours.")

        print(f"\n  Full send log saved to  : {SENDING_LOG}")

        next_week     = week_number + 1
        next_start, _ = get_week_range(next_week)
        if next_start < total_rows:
            print(f"\n  Next step:")
            print(f"    python main_pipeline.py --week {next_week}")
        else:
            print(f"\n  All {total_rows} users covered!")

    print(f"{'='*65}\n")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    global BATCH_SIZE

    parser = argparse.ArgumentParser(
        description="AstroVed Bulk WhatsApp Sender - Weekly Phase Pipeline"
    )
    parser.add_argument("--week",       type=int,   default=None)
    parser.add_argument("--preview",    action="store_true")
    parser.add_argument("--delay",      type=float, default=DEFAULT_DELAY,
                        help=f"Base seconds between sends (default: {DEFAULT_DELAY})")
    parser.add_argument("--status",     action="store_true")
    parser.add_argument("--batch-size", type=int,   default=BATCH_SIZE, dest="batch_size")

    args       = parser.parse_args()
    BATCH_SIZE = args.batch_size

    if args.status:
        show_status()
        return

    if args.week is None:
        parser.print_help()
        print()
        print("  QUICK EXAMPLES:")
        print("  python main_pipeline.py --week 1              # Send users 1-500")
        print("  python main_pipeline.py --week 1 --preview    # Preview only")
        print("  python main_pipeline.py --status              # Check progress")
        print("  python main_pipeline.py --week 1 --delay 15   # 15s gap (safer)")
        print()
        return

    if args.week < 1:
        print("\n  ERROR: --week must be 1 or higher.\n")
        return

    run_week(week_number=args.week, preview=args.preview, delay=args.delay)


if __name__ == "__main__":
    main()