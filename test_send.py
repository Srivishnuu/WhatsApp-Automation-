"""
test_send.py — Send a test message to 2 specific members.
==========================================================
Steps:
  1. Fill in the 2 users below with real name, moon sign, nakshatra, mobile.
  2. Run:  python test_send.py
  3. Check your phone — message should arrive within 30 seconds.
"""

import time
from whatsapp.template_sender import send_template

# ── Edit these 2 users with real details ─────────────────────────────────────
TEST_USERS = [

   
    {
        "name":      "Kishore",                # ← full name
        "moon":      "Aquarius",        # ← moon sign (lowercase)
        "nakshatra": "Purva Bhadrapada",       # ← nakshatra (lowercase)
        "mobile":    "8760619607",   # Somashekar CK,Aquarius,Purva Bhadrapada,9740091526       
    },
     {
        "name":      "Sathish",                # ← full name
        "moon":      "Pisces",        # ← moon sign (lowercase)
        "nakshatra": "Revati",       # ← nakshatra (lowercase)
        "mobile":    "9884309294",   # Somashekar CK,Aquarius,Purva Bhadrapada,9740091526       
    }
    
]



SEND_DELAY = 6.0   # seconds between sends — keep at 3s minimum
# ─────────────────────────────────────────────────────────────────────────────


def main():
    print("\n" + "=" * 65)
    print("  TEST RUN — 2 members")
    print("=" * 65 + "\n") 
    

    # Safety check — skip if placeholder number still present
    for user in TEST_USERS:
        if "XXXXXXXXX" in user["mobile"]:
            print(f"  ERROR: Placeholder mobile found for '{user['name']}'.")
            print(f"         Edit TEST_USERS above with a real 10-digit number.\n")
            return

    results = {"delivered": 0, "failed": 0}
    failed_list = []

    for i, user in enumerate(TEST_USERS, start=1):
        print(f"  [{i}/{len(TEST_USERS)}]  {user['name']}  |  "
              f"{user['moon'].title()} Moon  |  "
              f"{user['nakshatra'].title()} Nakshatra  |  "
              f"+91 {user['mobile']}")

        success, error_code = send_template(
            name=user["name"],
            moon=user["moon"],
            nakshatra=user["nakshatra"],
            mobile=user["mobile"],
        )

        if success:
            print(f"  DELIVERED\n")
            results["delivered"] += 1
        else:
            print(f"  FAILED  —  error code: {error_code}\n")
            results["failed"] += 1
            failed_list.append((user["name"], user["mobile"], error_code))

        if i < len(TEST_USERS):
            print(f"  Waiting {SEND_DELAY}s before next send...\n")
            time.sleep(SEND_DELAY)

    # ── Summary ───────────────────────────────────────────────────────────────
    print("=" * 65)
    print(f"  RESULT  —  {results['delivered']} delivered  /  {results['failed']} failed")

    if failed_list:
        print(f"\n  Failed:")
        for name, mobile, code in failed_list:
            print(f"    {name} ({mobile})  —  error {code}")
        print()
        print("  Common fixes:")
        print("    131052 — template not yet approved by Meta, wait and retry")
        print("    131026 — number not on WhatsApp or unreachable")
        print("    131049 — content similarity, the new code retries automatically")
        print("    100    — special chars in a variable, check config.py")
        print("    unconfigured_template — set UNIVERSAL_TEMPLATE_ID in .env")

    if results["delivered"] == len(TEST_USERS):
        print()
        print("  Both messages delivered successfully.")
        print("  Next step: python main_pipeline.py --preview")

    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()