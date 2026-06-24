"""
db_conn.py — Pull active customers from MSSQL → data/customer_data.csv
=======================================================================
Run once before validate_numbers.py to refresh your contact list.

Usage:
    python db_conn.py

Requires in .env:
DB_SERVER, DB_NAME, DB_USERNAME, DB_PASSWORD

"""

import os
import pyodbc
import pandas as pd
from dotenv import load_dotenv 

load_dotenv()

SERVER   = os.getenv("DB_SERVER")
DATABASE = os.getenv("DB_NAME")
USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")

ACTIVE_DAYS = 90
OUTPUT_CSV  = "data/customer_data.csv"

QUERY = f"""
WITH RankedData AS (
    SELECT
        up.CustomerId                        AS Cust_Id,
        up.FirstName + ' ' + up.LastName     AS Cust_Name,
        up.MoonSign                          AS Moon_sign,
        up.Nakshatra,
        mv.MobileNo                          AS Mobile_Number,
        ROW_NUMBER() OVER (
            PARTITION BY up.CustomerId, mv.MobileNo
            ORDER BY up.CustomerId
        ) AS rn
    FROM  Vaaak.VW_UserProfile       up
    JOIN  Vaaak.MobileVerification   mv
          ON up.CustomerId = mv.CustomerId
    WHERE mv.IsMobileNoVerified = 1
      AND mv.CountryCode       = '+91'
      AND up.LastLoginDate     >= DATEADD(DAY, -{ACTIVE_DAYS}, GETDATE())
)
SELECT Cust_Id, Cust_Name, Moon_sign, Nakshatra, Mobile_Number
FROM   RankedData
WHERE  rn = 1;
"""            
def main():
    print(f"\n{'='*60}")
    print(f"  DB Export — AstroVed Customer Data")
    print(f"  Server   : {SERVER}")
    print(f"  Database : {DATABASE}")
    print(f"{'='*60}\n")

    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={SERVER};DATABASE={DATABASE};"
        f"UID={USERNAME};PWD={PASSWORD};"
        "TrustServerCertificate=yes;"
    )

    conn = None
    df   = None

    try:
        conn = pyodbc.connect(conn_str)
        print("  ✅ Connected to database")
        df = pd.read_sql(QUERY, conn)
        print(f"  📊 Fetched {len(df)} active users (last {ACTIVE_DAYS} days)")

    except Exception as e:
        print(f"  ❌ Database error: {e}")

    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

    if df is not None:
        os.makedirs("data", exist_ok=True)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"\n  ✅ Saved → {OUTPUT_CSV}")
        print(f"\n  ▶  Next step:")
        print(f"     python validate_numbers.py")
    else:
        print(f"\n  ❌ Export failed — CSV not created")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()