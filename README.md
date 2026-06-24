# AstroVed WhatsApp Marketing Automation

## Overview

AstroVed WhatsApp Marketing Automation is a Python-based bulk messaging platform designed to deliver personalized astrology insights to customers through WhatsApp using the Gallabox API.

The system automatically:

* Fetches active customer data from Microsoft SQL Server
* Processes customer astrology information (Moon Sign & Nakshatra)
* Generates personalized astrology messages
* Maps users to relevant AstroVed free tools and services
* Sends approved WhatsApp template messages through Gallabox
* Tracks delivery status, failures, and campaign progress
* Supports phased weekly campaign execution

---

## Features

### Customer Data Extraction

* Connects to Microsoft SQL Server
* Fetches active users from AstroVed database
* Exports customer data into CSV format
* Removes duplicate customer records

### Astrology Personalization

* Moon Sign normalization
* Nakshatra normalization
* Astrology insight generation
* Personalized horoscope recommendations
* Dynamic free tool recommendations

### WhatsApp Automation

* Gallabox WhatsApp API integration
* Approved Meta template messaging
* Bulk campaign execution
* Weekly phased sending strategy
* Automatic delivery tracking

### Safety & Rate Limiting

Built to reduce Meta WhatsApp restrictions:

* Warm-up sending strategy
* Random send interval jitter
* Hourly pause mechanism
* Circuit breaker for error handling
* Safe sending time windows

### Reporting & Tracking

* Sent number tracking
* Failed delivery logs
* Complete sending logs
* Campaign progress monitoring
* Week-wise batch tracking

---

## Project Architecture

```text
Microsoft SQL Server
        │
        ▼
db_conn.py
(Fetch Customer Data)
        │
        ▼
customer_data.csv
        │
        ▼
validate_numbers.py
(Number Verification)
        │
        ▼
main_pipeline.py
(Message Processing)
        │
        ▼
Gallabox API
        │
        ▼
WhatsApp Delivery
        │
        ▼
Customer Receives Message
```

---

## Project Structure

```text
project/
│
├── config.py
├── db_conn.py
├── validate_numbers.py
├── main_pipeline.py
├── test_send.py
│
├── data/
│   ├── customer_data.csv
│   ├── valid_numbers.csv
│   ├── invalid_numbers.csv
│   ├── sent_numbers.csv
│   ├── failed_numbers.csv
│   └── sending_log.csv
│
├── whatsapp/
│   └── template_sender.py
│
├── .env
├── requirements.txt
└── README.md
```

---

## Workflow

### Step 1: Export Customer Data

Fetch active users from SQL Server.

```bash
python db_conn.py
```

Output:

```text
data/customer_data.csv
```

---

### Step 2: Validate WhatsApp Numbers

Verify whether customer numbers exist on WhatsApp.

```bash
python validate_numbers.py
```

Outputs:

```text
data/valid_numbers.csv
data/invalid_numbers.csv
```

---

### Step 3: Test Message Delivery

Send messages to a few test users before running a campaign.

```bash
python test_send.py
```

---

### Step 4: Preview Campaign

Preview the batch without sending messages.

```bash
python main_pipeline.py --week 1 --preview
```

---

### Step 5: Launch Campaign

Start sending WhatsApp messages.

```bash
python main_pipeline.py --week 1
```

---

### Step 6: Monitor Status

Check campaign progress.

```bash
python main_pipeline.py --status
```

---

## WhatsApp Template

### Template Name

```text
whatsapp_automation1
```

### Message Format

```text
Hi {{1}}! 🌙
{{2}}

🌟 Based on your rashi & nakshatra:
{{3}}

Explore more astrology insights.
By AstroVed Team
```

### Variables

| Variable | Description                           |
| -------- | ------------------------------------- |
| {{1}}    | Customer Name + Moon Sign + Nakshatra |
| {{2}}    | Personalized Astrology Insight        |
| {{3}}    | Recommended AstroVed Tool URL         |

---

## Campaign Strategy

The platform sends messages in weekly batches.

Example:

```text
Week 1 → Users 1 - 500
Week 2 → Users 501 - 1000
Week 3 → Users 1001 - 1500
...
```

Benefits:

* Reduces WhatsApp spam risk
* Improves delivery quality
* Maintains sender reputation
* Easier campaign tracking

---

## Safety Mechanisms

### Warm-Up Sending

First messages are sent slowly to establish trust with Meta.

### Random Delay

Random intervals prevent robotic patterns.

### Hourly Pause

Automatic pauses after a configurable number of messages.

### Circuit Breaker

Pauses campaigns when excessive Meta errors occur.

### Sending Window

Messages are only sent during configured safe hours.

---

## Environment Variables

Create a `.env` file.

```env
# Database

DB_SERVER=
DB_NAME=
DB_USERNAME=
DB_PASSWORD=

# Gallabox

GALLABOX_API_KEY=
GALLABOX_API_SECRET=
CHANNEL_ID=
UNIVERSAL_TEMPLATE_ID=

# Optional AI Integration

ANTHROPIC_API_KEY=
```

---

## Output Files

### customer_data.csv

Customer records fetched from database.

### valid_numbers.csv

Verified WhatsApp users.

### invalid_numbers.csv

Invalid or unreachable numbers.

### sent_numbers.csv

Permanent delivery tracking.

### failed_numbers.csv

Failed message records.

### sending_log.csv

Complete campaign logs.

---

## Example Message

```text
Hi Ramesh | Aries Moon | Ashwini Nakshatra 🌙

Bold Aries Moon energy lights up your day with confidence and action.

🌟 Based on your rashi & nakshatra:
https://www.astroved.com/Report.aspx?type=numerology

Explore more astrology insights.

By AstroVed Team
```

---

## Technology Stack

* Python 3.x
* Microsoft SQL Server
* PyODBC
* Pandas
* Requests
* Gallabox WhatsApp API
* dotenv

---

## Future Enhancements

* AI-powered astrology content generation
* Dynamic campaign scheduling
* CRM integration
* Image generation for campaigns
* Dashboard analytics
* Retry automation for failed messages
* Customer engagement scoring

---

## Author

Developed for AstroVed Marketing Automation & WhatsApp Customer Engagement Campaigns.

---

## Disclaimer

This project is intended for approved WhatsApp template messaging and customer engagement campaigns. Ensure compliance with WhatsApp Business Platform policies, Gallabox guidelines, and customer consent requirements before sending bulk messages.
