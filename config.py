"""
config.py — Central configuration for AstroVed WhatsApp Automation
===================================================================

TEMPLATE DESIGN (3 variables — matches your screenshot exactly):
─────────────────────────────────────────────────────────────────
TEMPLATE NAME : whatsapp_automation1
CATEGORY      : MARKETING
LANGUAGE      : English (en)
HEADER        : NONE (no image — reduces Meta 131049 flag rate)

BODY (copy this EXACTLY into Gallabox):
─────────────────────────────────────────────────────────────────
Hi {{1}}! 🌙
{{2}}

🌟 Based on your rashi & nakshatra:
{{3}}

Explore more astrology insights.
By AstroVed Team
─────────────────────────────────────────────────────────────────

BUTTON:
  Type        : URL
  Button text : Explore Now
  URL         : https://www.astroved.com/horoscopes

SAMPLE VALUES (paste these in Gallabox during submission):
  {{1}} : Kishore | Virgo Moon | Hasta Nakshatra
  {{2}} : Dynamic Virgo Moon energy brings clarity and focus to your work today. Take one decisive step forward and trust the momentum you have built.
  {{3}} : https://www.astroved.com/Report.aspx?type=numerology&promo=WA_Auto

AFTER TEMPLATE APPROVAL:
  1. Copy the Template ID from Gallabox
  2. Add to your .env file:
       UNIVERSAL_TEMPLATE_ID=paste_your_id_here
  3. Confirm UNIVERSAL_TEMPLATE_NAME below matches exactly what you named it in Gallabox

WHY 3 VARIABLES (not 4):
  The screenshot shows your working template uses exactly 3 body variables:
    {{1}} = Header line  (Name | Moon | Nakshatra)
    {{2}} = AI insight   (the personalised message body)
    {{3}} = Tool URL     (the free tool link)
  Using the fewest variables reduces Meta review friction.

URL FIX NOTE:
  All URLs now use & (not ?) to append promo= after an existing query string.
  Wrong : https://example.com/page?type=xyz?promo=WA_Auto   ← double ? breaks URL
  Right : https://example.com/page?type=xyz&promo=WA_Auto   ← correct & separator
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Gallabox Credentials ─────────────────────────────────────────────────────
GALLABOX_API_KEY    = os.getenv("GALLABOX_API_KEY")
GALLABOX_API_SECRET = os.getenv("GALLABOX_API_SECRET")
CHANNEL_ID          = os.getenv("CHANNEL_ID")

# ── Universal Template ───────────────────────────────────────────────────────
UNIVERSAL_TEMPLATE_NAME = "whatsapp_automation1"
UNIVERSAL_TEMPLATE_ID   = os.getenv("UNIVERSAL_TEMPLATE_ID", "69fad531fd44328dcdafec96")

# ── Valid moon signs ─────────────────────────────────────────────────────────
VALID_MOON_SIGNS = {
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
}

# ── Moon sign aliases ────────────────────────────────────────────────────────
MOON_SIGN_ALIASES = {
    "sagitarius": "sagittarius", "saggitarius": "sagittarius",
    "saggittarius": "sagittarius", "dhanu": "sagittarius",
    "capricon": "capricorn", "capricornn": "capricorn", "makara": "capricorn",
    "aquarious": "aquarius", "kumbha": "aquarius",
    "tarus": "taurus", "tauras": "taurus", "vrishabha": "taurus",
    "gemni": "gemini", "mithuna": "gemini",
    "scorpion": "scorpio", "vrishchika": "scorpio",
    "ares": "aries", "mesha": "aries",
    "libera": "libra", "tula": "libra",
    "karka": "cancer", "karkata": "cancer", "kataka": "cancer",
    "simha": "leo", "sinh": "leo",
    "kanya": "virgo",
    "meena": "pisces", "meen": "pisces",
}


def resolve_moon_sign(raw: str) -> str:
    """Normalise any moon sign string to clean lowercase canonical key."""
    if not raw:
        return ""
    cleaned = raw.strip().lower()
    if cleaned in VALID_MOON_SIGNS:
        return cleaned
    if cleaned in MOON_SIGN_ALIASES:
        return MOON_SIGN_ALIASES[cleaned]
    for sign in VALID_MOON_SIGNS:
        if sign in cleaned:
            return sign
    return cleaned


# ══════════════════════════════════════════════════════════════════════════════
# FREE TOOLS  (used in var3 of the WhatsApp template)
#
# URL RULES — strictly followed to avoid broken links in messages:
#   • If the base URL has NO query string  → append ?promo=WA_Auto
#   • If the base URL already has ?param=x → append &promo=WA_Auto
#   • NEVER use ?promo= after another ?param= — that creates a double-? URL
# ══════════════════════════════════════════════════════════════════════════════
FREE_TOOLS = {
    # ── Core astrology reports ────────────────────────────────────────────
    "numerology": {
        "label": "Free Numerology Reading",
        "url":   "https://www.astroved.com/Report.aspx?type=numerology&promo=WA_Auto",
    },
    "horoscope": {
        "label": "Free Daily Horoscope",
        "url":   "https://www.astroved.com/horoscopes?promo=WA_Auto",
    },
    "kundli": {
        "label": "Free Kundli / Birth Chart",
        "url":   "https://www.astroved.com/Report.aspx?type=chart&promo=WA_Auto",
    },
    "nakshatra_report": {
        "label": "Free Nakshatra Report",
        "url":   "https://www.astroved.com/Report.aspx?type=birthstar&promo=WA_Auto",
    },
    "compatibility": {
        "label": "Free Love Compatibility Reading",
        "url":   "https://www.astroved.com/astropedia/en/freetools/love-calculator?promo=WA_Auto",
    },
    "transit": {
        "label": "Free Planet Transit Report",
        "url":   "https://www.astroved.com/astrology-services?promo=WA_Transit_Report",
    },
    "lucky_number": {
        "label": "Free Lucky Number Reading",
        "url":   "https://www.astroved.com/astropedia/en/freetools/lucky-numbers?promo=WA_Auto",
    },
    "rudraksha": {
        "label": "Free Rudraksha Recommendation",
        "url":   "https://www.astroved.com/rudraksha-beads?promo=WA_Auto",
    },
    "mantra": {
        "label": "Free Personalised Mantra Guide",
        "url":   "https://www.astroved.com/astropedia/en/mantras?promo=WA_Auto",
    },
    "yantra": {
        "label": "Free Yantra Recommendation",
        "url":   "https://www.astroved.com/yantra-c2.aspx?promo=WA_Auto",
    },
    "gemstone": {
        "label": "Free Gemstone Recommendation",
        "url":   "https://www.astroved.com/astropedia/en/freetools/gemstone?promo=WA_Auto",
    },
    "pooja": {
        "label": "Free Pooja Recommendation",
        "url":   "https://www.astroved.com/astropedia/en/virtual-pooja?promo=WA_Auto",
    },
    # ── Additional free tools (from Excel sheet) ─────────────────────────
    "birth_date_compatibility": {
        "label": "Free Birth Date Compatibility",
        "url":   "https://www.astroved.com/astropedia/en/freetools/birth-date-compatibility?promo=WA_Auto",
    },
    "baby_name_finder": {
        "label": "Free Baby Name Finder",
        "url":   "https://www.astroved.com/astropedia/en/babynames?promo=WA_Auto",
    },
    "hora_watch": {
        "label": "Free Hora Watch",
        "url":   "https://www.astroved.com/astropedia/en/freetools/hora?promo=WA_Auto",
    },
    "naga_dosha": {
        "label": "Free Naga Dosha Check",
        "url":   "https://www.astroved.com/astropedia/en/freetools/naga-dosha?promo=WA_Auto",
    },
    "nakshatra_porutham": {
        "label": "Free Nakshatra Porutham",
        "url":   "https://www.astroved.com/astropedia/en/freetools/nakshatra-porutham?promo=WA_Auto",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# DAILY HOROSCOPE URLS  (rashi-specific — used when theme = "horoscope")
# ══════════════════════════════════════════════════════════════════════════════
DAILY_HOROSCOPE_URLS = {
    "aries":       "https://www.astroved.com/horoscopes/daily-horoscope/aries?promo=WA_Auto",
    "taurus":      "https://www.astroved.com/horoscopes/daily-horoscope/taurus?promo=WA_Auto",
    "gemini":      "https://www.astroved.com/horoscopes/daily-horoscope/gemini?promo=WA_Auto",
    "cancer":      "https://www.astroved.com/horoscopes/daily-horoscope/cancer?promo=WA_Auto",
    "leo":         "https://www.astroved.com/horoscopes/daily-horoscope/leo?promo=WA_Auto",
    "virgo":       "https://www.astroved.com/horoscopes/daily-horoscope/virgo?promo=WA_Auto",
    "libra":       "https://www.astroved.com/horoscopes/daily-horoscope/libra?promo=WA_Auto",
    "scorpio":     "https://www.astroved.com/horoscopes/daily-horoscope/scorpio?promo=WA_Auto",
    "sagittarius": "https://www.astroved.com/horoscopes/daily-horoscope/sagittarius?promo=WA_Auto",
    "capricorn":   "https://www.astroved.com/horoscopes/daily-horoscope/capricorn?promo=WA_Auto",
    "aquarius":    "https://www.astroved.com/horoscopes/daily-horoscope/aquarius?promo=WA_Auto",
    "pisces":      "https://www.astroved.com/horoscopes/daily-horoscope/pisces?promo=WA_Auto",
}

# ══════════════════════════════════════════════════════════════════════════════
# ASTROVED PAID SERVICES  (for future upsell campaigns)
# ══════════════════════════════════════════════════════════════════════════════
ASTROVED_SERVICES = {
    # ── Rituals & poojas ──────────────────────────────────────────────────
    "coconut_smashing": {
        "label": "Coconut Smashing",
        "url":   "https://www.astroved.com/us/specials/coconut-smash?promo=WA_Auto",
    },
    "pradosham": {
        "label": "Pradosham",
        "url":   "https://www.astroved.com/remedies/pradosham?promo=WA_Auto",
    },
    "instant_pooja_homas": {
        "label": "Instant Pooja and Homas",
        "url":   "https://www.astroved.com/instant-pooja?promo=WA_Auto",
    },
    "special_poojas": {
        "label": "Special Poojas",
        "url":   "https://www.astroved.com/pooja-c11.aspx?promo=WA_Auto",
    },
    "special_abishekham": {
        "label": "Special Abishekham",
        "url":   "https://www.astroved.com/abishekam-hydration-pooja--c375.aspx?promo=WA_Auto",
    },
    "cow_feeding": {
        "label": "Cow Feeding Program",
        "url":   "https://www.astroved.com/us/specials/cow-feeding-program?promo=WA_Auto",
    },
    # ── Consultations ─────────────────────────────────────────────────────
    "astrology_services": {
        "label": "Astrology Services",
        "url":   "https://www.astroved.com/astrology-services?promo=WA_Auto",
    },
    "rameshwaram_rituals": {
        "label": "Rameshwaram Rituals",
        "url":   "https://www.astroved.com/remedies/rameswaram-rituals?promo=WA_Auto",
    },
    "grand_homas": {
        "label": "Grand Homas",
        "url":   "https://www.astroved.com/us/specials/grand-homas?promo=WA_Auto",
    },
    "astroved_temple": {
        "label": "AstroVed Temple",
        "url":   "https://www.astroved.com/temple/?promo=WA_Auto",
    },
    "nadi_astrology": {
        "label": "Nadi Astrology",
        "url":   "https://www.astroved.com/nadi/nadi-astrology?promo=WA_Auto",
    },
    "instant_insight": {
        "label": "Instant Insight (Prasna)",
        "url":   "https://www.astroved.com/prasnaastrology.aspx?promo=WA_Auto",
    },
    "talk_to_astrologer": {
        "label": "Talk to Astrologer",
        "url":   "https://www.astroved.com/astrovedspeaks/talk-to-astrologer?promo=WA_Auto",
    },
    "palm_reading": {
        "label": "Palm Reading",
        "url":   "https://www.astroved.com/palm-reading?promo=WA_Auto",
    },
    # ── Live astrologer sessions ──────────────────────────────────────────
    "live_astrology_consultation": {
        "label": "Live Astrology Consultation",
        "url":   "https://www.astroved.com/AstrologerScheduler.aspx?id=115&promo=WA_Auto",
    },
    "astrologer_vijayalakshmi": {
        "label": "Astrologer VijayaLakshmi",
        "url":   "https://www.astroved.com/AstrologerScheduler.aspx?id=63143&promo=WA_Auto",
    },
    "agastya_live_channel_reading": {
        "label": "Agastya Live Channel Reading",
        "url":   "https://www.astroved.com/AstrologerScheduler.aspx?id=50579&promo=WA_Auto",
    },
    "goddess_angali_reading": {
        "label": "Goddess Angali Reading",
        "url":   "https://www.astroved.com/us/specials/goddess-angali-reading?promo=WA_Auto",
    },
    "karuppasamy_reading": {
        "label": "Karuppasamy Divine Reading & Remedies",
        "url":   "https://www.astroved.com/us/specials/karuppasamy-divine-reading-remedies-program?promo=WA_Auto",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# PRODUCTS  (physical / e-commerce items)
# ══════════════════════════════════════════════════════════════════════════════
PRODUCTS = {
    "rudraksha_products": {
        "label": "Rudraksha Beads",
        "url":   "https://www.astroved.com/rudraksha-beads?promo=WA_Auto",
    },
    "statues": {
        "label": "Statues",
        "url":   "https://www.astroved.com/statue-c95.aspx?promo=WA_Auto",
    },
    "malas": {
        "label": "Malas",
        "url":   "https://www.astroved.com/malas-c22.aspx?promo=WA_Auto",
    },
    "bracelets": {
        "label": "Bracelets",
        "url":   "https://www.astroved.com/bracelets-c145.aspx?promo=WA_Auto",
    },
    "pendants": {
        "label": "Pendants",
        "url":   "https://www.astroved.com/pendants-c392.aspx?promo=WA_Auto",
    },
    "incense_sticks": {
        "label": "Incense Sticks (Agarbatti)",
        "url":   "https://www.astroved.com/agarbatti-incense-sticks?promo=WA_Auto",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# ASTROVED TEMPLE — individual deity pages
# ══════════════════════════════════════════════════════════════════════════════
TEMPLE_PAGES = {
    "ganesha_statue":        "https://www.astroved.com/temple/ganesha-statue/?promo=WA_Auto",
    "vyasa_draupadi":        "https://www.astroved.com/temple/vyasa-draupadi/?promo=WA_Auto",
    "shiva_lingam":          "https://www.astroved.com/temple/shiva-lingam/?promo=WA_Auto",
    "dhanvantri":            "https://www.astroved.com/temple/dhanvantri/?promo=WA_Auto",
    "nandi":                 "https://www.astroved.com/temple/nandi/?promo=WA_Auto",
    "varahi_devi":           "https://www.astroved.com/temple/varahi-devi/?promo=WA_Auto",
    "pratyangira_devi":      "https://www.astroved.com/temple/pratyangira-devi/?promo=WA_Auto",
    "lakshmi_devi":          "https://www.astroved.com/temple/lakshmi-devi/?promo=WA_Auto",
    "murugan":               "https://www.astroved.com/temple/murugan/?promo=WA_Auto",
    "maha_vishnu":           "https://www.astroved.com/temple/maha-vishnu/?promo=WA_Auto",
    "goddess_angali":        "https://www.astroved.com/temple/goddess-angali/?promo=WA_Auto",
    "shreem_brzee_lakshmi":  "https://www.astroved.com/temple/shreem-brzee-lakshmi/?promo=WA_Auto",
    "ganesha_anjenaya":      "https://www.astroved.com/temple/ganesha-anjenaya/?promo=WA_Auto",
    "saraswati":             "https://www.astroved.com/temple/saraswati/?promo=WA_Auto",
    "bala_tripura_sundari":  "https://www.astroved.com/temple/bala-tripura-sundari/?promo=WA_Auto",
    "shirdi_sai_baba":       "https://www.astroved.com/temple/shirdi-sai-baba/?promo=WA_Auto",
    "agastya_rishi":         "https://www.astroved.com/temple/agastya-rishi/?promo=WA_Auto",
    "chakrathalwar":         "https://www.astroved.com/temple/chakrathalwar/?promo=WA_Auto",
    "ayyappa":               "https://www.astroved.com/temple/ayyappa/?promo=WA_Auto",
    "siddhi_buddhi_ganapathi": "https://www.astroved.com/temple/siddhi-buddhi-ganapathi/?promo=WA_Auto",
    "lord_kuber":            "https://www.astroved.com/temple/lord-kuber/?promo=WA_Auto",
    "hayagriva":             "https://www.astroved.com/temple/hayagriva/?promo=WA_Auto",
    "maa_durga":             "https://www.astroved.com/temple/maa-durga/?promo=WA_Auto",
    "kaala_bhairava":        "https://www.astroved.com/temple/kaala-bhairava/?promo=WA_Auto",
    "hanuman":               "https://www.astroved.com/temple/hanuman/?promo=WA_Auto",
    "heramba_ganapati":      "https://www.astroved.com/temple/heramba-ganapati/?promo=WA_Auto",
    "lord_bala_murugan":     "https://www.astroved.com/temple/lord-bala-murugan/?promo=WA_Auto",
    "kamadhenu_cow":         "https://www.astroved.com/temple/kamadhenu-cow/?promo=WA_Auto",
    "maha_meru":             "https://www.astroved.com/temple/maha-meru/?promo=WA_Auto",
    "haridra_ganapati":      "https://www.astroved.com/temple/haridra-ganapati/?promo=WA_Auto",
    "kshipra_ganapathi":     "https://www.astroved.com/temple/kshipra-ganapathi/?promo=WA_Auto",
    "narasimha":             "https://www.astroved.com/temple/narasimha/?promo=WA_Auto",
    "shri_krishna":          "https://www.astroved.com/temple/shri-krishna/?promo=WA_Auto",
    "lakshmi_kuberar":       "https://www.astroved.com/temple/lakshmi-kuberar/?promo=WA_Auto",
    "natarajar":             "https://www.astroved.com/temple/natarajar/?promo=WA_Auto",
    "lakshmi_narayan":       "https://www.astroved.com/temple/lakshmi-narayan/?promo=WA_Auto",
    "nalvar":                "https://www.astroved.com/temple/nalvar/?promo=WA_Auto",
    "pachamukhi_ganesha":    "https://www.astroved.com/temple/pachamukhi-ganesha/?promo=WA_Auto",
    "sharabha":              "https://www.astroved.com/temple/sharabha/?promo=WA_Auto",
}

# ══════════════════════════════════════════════════════════════════════════════
# NAKSHATRA → FREE TOOL MAPPING
# ══════════════════════════════════════════════════════════════════════════════
NAKSHATRA_FREE_TOOL = {
    "ashwini":              "rudraksha",
    "bharani":              "numerology",
    "krittika":             "yantra",
    "rohini":               "gemstone",
    "mrigashira":           "compatibility",
    "ardra":                "transit",
    "punarvasu":            "horoscope",
    "pushya":               "mantra",
    "ashlesha":             "kundli",
    "magha":                "pooja",
    "purva phalguni":       "lucky_number",
    "uttara phalguni":      "nakshatra_report",
    "hasta":                "numerology",
    "chitra":               "yantra",
    "swati":                "compatibility",
    "vishakha":             "transit",
    "anuradha":             "mantra",
    "jyeshtha":             "rudraksha",
    "mula":                 "pooja",
    "purva ashadha":        "gemstone",
    "uttara ashadha":       "lucky_number",
    "shravana":             "mantra",
    "dhanishta":            "yantra",
    "shatabhisha":          "numerology",
    "purva bhadrapada":     "yantra",
    "uttara bhadrapada":    "pooja",
    "revati":               "compatibility",
}

# ── Moon sign → fallback free tool (when nakshatra unknown) ──────────────────
MOON_FREE_TOOL = {
    "aries":       "horoscope",
    "taurus":      "gemstone",
    "gemini":      "numerology",
    "cancer":      "kundli",
    "leo":         "pooja",
    "virgo":       "nakshatra_report",
    "libra":       "compatibility",
    "scorpio":     "transit",
    "sagittarius": "lucky_number",
    "capricorn":   "rudraksha",
    "aquarius":    "yantra",
    "pisces":      "mantra",
}

# ── Nakshatra aliases ────────────────────────────────────────────────────────
NAKSHATRA_ALIASES = {
    "ashwani": "ashwini", "aswini": "ashwini", "aswani": "ashwini",
    "bharni": "bharani",
    "kritika": "krittika", "karthika": "krittika",
    "mrigasira": "mrigashira", "mrigasheera": "mrigashira",
    "arudra": "ardra",
    "punarpusam": "punarvasu",
    "poosam": "pushya",
    "ayilyam": "ashlesha",
    "makam": "magha",
    "pooram": "purva phalguni",
    "uthiram": "uttara phalguni",
    "chitira": "chitra", "chithira": "chitra",
    "visakha": "vishakha",
    "anusham": "anuradha",
    "kettai": "jyeshtha",
    "moolam": "mula",
    "pooradam": "purva ashadha",
    "uthiradam": "uttara ashadha",
    "thiruvonam": "shravana",
    "avittam": "dhanishta",
    "sathayam": "shatabhisha", "sadayam": "shatabhisha",
    "poorattathi": "purva bhadrapada",
    "uthirattathi": "uttara bhadrapada",
    "revathi": "revati",
}


def resolve_nakshatra(raw: str) -> str:
    """Normalise nakshatra name to canonical lowercase key."""
    if not raw:
        return ""
    cleaned = raw.strip().lower()
    if cleaned in NAKSHATRA_FREE_TOOL:
        return cleaned
    if cleaned in NAKSHATRA_ALIASES:
        return NAKSHATRA_ALIASES[cleaned]
    for nak in NAKSHATRA_FREE_TOOL:
        if nak in cleaned or cleaned in nak:
            return nak
    return cleaned


# ── Helper: get the rashi-specific daily horoscope URL ───────────────────────
def get_daily_horoscope_url(moon_key: str) -> str:
    """Return personalised daily horoscope URL for a given moon sign."""
    return DAILY_HOROSCOPE_URLS.get(moon_key, FREE_TOOLS["horoscope"]["url"])


# ══════════════════════════════════════════════════════════════════════════════
# MOON SIGN INSIGHT SEEDS
# ══════════════════════════════════════════════════════════════════════════════
MOON_MESSAGES = {
    "aries":       "Bold Aries Moon energy lights up your day with fire and drive. This is the perfect time to take decisive action and move toward what you truly want.",
    "taurus":      "Steady Taurus Moon energy grounds you with calm and purpose today. Trust your instincts and invest your energy in what brings lasting value.",
    "gemini":      "Bright Gemini Moon energy sharpens your wit and curiosity today. Conversations flow with ease and the right connections bring exciting new doors.",
    "cancer":      "Gentle Cancer Moon energy deepens your intuition and compassion today. Listening to your inner voice brings clarity and the right path reveals itself.",
    "leo":         "Radiant Leo Moon energy fills you with warmth and creative power today. Stepping forward with confidence allows your natural brilliance to shine for all.",
    "virgo":       "Clear Virgo Moon energy brings focus and precision to everything you do. Channelling your attention on details today leads to meaningful and lasting results.",
    "libra":       "Harmonious Libra Moon energy surrounds you with grace and balance today. Thoughtful choices made with care create beautiful outcomes for the days ahead.",
    "scorpio":     "Intense Scorpio Moon energy gifts you with deep insight and perception today. Trusting what you sense beneath the surface guides you toward powerful decisions.",
    "sagittarius": "Expansive Sagittarius Moon energy opens your mind to bold new horizons. Embracing optimism and exploring fresh ideas brings exciting progress on your journey.",
    "capricorn":   "Disciplined Capricorn Moon energy fuels steady and focused progress today. Each deliberate step forward builds the strong and meaningful life you are creating.",
    "aquarius":    "Visionary Aquarius Moon energy sparks original and innovative thinking today. An unconventional perspective brings exactly the fresh approach a situation needs.",
    "pisces":      "Sensitive Pisces Moon energy heightens your intuition and spiritual awareness. Trusting your inner knowing and the wisdom of your dreams guides you beautifully.",
}

# ══════════════════════════════════════════════════════════════════════════════
# NAKSHATRA INSIGHT SEEDS
# ══════════════════════════════════════════════════════════════════════════════
NAKSHATRA_INSIGHTS = {
    "ashwini":             "Swift Ashwini Nakshatra energy accelerates fresh beginnings and bold new starts for you today.",
    "bharani":             "Transformative Bharani Nakshatra power invites you to embrace meaningful change with courage and grace.",
    "krittika":            "Sharp Krittika Nakshatra clarity helps you cut through confusion and focus on what truly matters.",
    "rohini":              "Nurturing Rohini Nakshatra energy attracts abundance as your creativity and natural charm draw blessings in.",
    "mrigashira":          "Curious Mrigashira Nakshatra energy sparks wonder today as following what excites you leads somewhere beautiful.",
    "ardra":               "Renewing Ardra Nakshatra energy brings transformation through release so trust the changes unfolding around you.",
    "punarvasu":           "Hopeful Punarvasu Nakshatra energy restores what was lost as things naturally find their way back to you.",
    "pushya":              "Blessed Pushya Nakshatra energy supports all your goals today as nurturing your dreams with patience brings reward.",
    "ashlesha":            "Perceptive Ashlesha Nakshatra energy deepens your intuition so trust that your keen insight is your greatest gift.",
    "magha":               "Powerful Magha Nakshatra energy connects you to the strength of your lineage so stand tall in who you are.",
    "purva phalguni":      "Joyful Purva Phalguni Nakshatra energy invites celebration and creative expression today so let yourself shine freely.",
    "uttara phalguni":     "Devoted Uttara Phalguni Nakshatra energy supports commitment and dedication so your steady effort brings beautiful rewards.",
    "hasta":               "Skilled Hasta Nakshatra energy blesses your hands and mind today as focused work creates something truly meaningful.",
    "chitra":              "Artistic Chitra Nakshatra energy stirs your creative vision so beauty in all its forms calls out to you today.",
    "swati":               "Independent Swati Nakshatra energy empowers you to chart your own course today with full confidence in your path.",
    "vishakha":            "Ambitious Vishakha Nakshatra energy fuels your determination today as staying focused brings your goal closer with each step.",
    "anuradha":            "Devoted Anuradha Nakshatra energy deepens bonds of friendship and loyalty today as your dedication is truly rewarded.",
    "jyeshtha":            "Strong Jyeshtha Nakshatra energy amplifies your natural leadership today so step forward and guide with quiet confidence.",
    "mula":                "Rooted Mula Nakshatra energy invites deep transformation today as going to the very core reveals your greatest gifts.",
    "purva ashadha":       "Unstoppable Purva Ashadha Nakshatra energy fills you with powerful momentum today as nothing can slow your forward progress.",
    "uttara ashadha":      "Victorious Uttara Ashadha Nakshatra energy builds lasting success today as your persistent effort is about to pay off.",
    "shravana":            "Wise Shravana Nakshatra energy opens the art of listening today as stillness and patience bring remarkable insight to you.",
    "dhanishta":           "Abundant Dhanishta Nakshatra energy resonates with rhythm and flow today so align with your natural pace and thrive.",
    "shatabhisha":         "Healing Shatabhisha Nakshatra energy activates your power to restore and renew so embrace your gift of transformation.",
    "purva bhadrapada":    "Fierce Purva Bhadrapada Nakshatra energy sparks deep transformation today so embrace the inner fire that drives you forward.",
    "uttara bhadrapada":   "Wise Uttara Bhadrapada Nakshatra energy brings calm depth and quiet strength today as your steady presence inspires everyone around you.",
    "revati":              "Protective Revati Nakshatra energy guides your journey safely today as you move forward knowing you are watched over and blessed.",
}