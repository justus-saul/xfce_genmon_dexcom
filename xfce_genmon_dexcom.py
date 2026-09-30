#!/usr/bin/env python3
import html
import json
import sys
from datetime import datetime
from pathlib import Path
from pydexcom import Dexcom

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
LOCALES_PATH = BASE_DIR / "locales.json"

ALERT_COLOR = "#ff4d4d"
TARGET_COLOR = "#4ade80"

current_translations = {}

def print_genmon(text, tooltip):
    print(f"<txt>{text}</txt>")
    print(f"<tool>{tooltip}</tool>")
    sys.exit(0)

def t(key, default="", **kwargs):
    template = current_translations.get(key, default)
    try:
        return template.format(**kwargs)
    except Exception:
        return template

if not CONFIG_PATH.is_file():
    print_genmon("Dexcom: Config missing", f"File not found: {CONFIG_PATH}")

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
except json.JSONDecodeError as exc:
    print_genmon("Dexcom: JSON error", f"Invalid JSON in config.json: {exc}")
except OSError as exc:
    print_genmon("Dexcom: File error", f"Failed reading config.json: {exc}")

lang = cfg.get("lang", "de")

if LOCALES_PATH.is_file():
    try:
        with open(LOCALES_PATH, "r", encoding="utf-8") as f:
            all_locales = json.load(f)
            current_translations = all_locales.get(lang, all_locales.get("de", {}))
    except Exception:
        pass

required_keys = ("username", "password")
missing_keys = [k for k in required_keys if k not in cfg]
if missing_keys:
    print_genmon(
        t("missing_params_title", "Dexcom: Config error"),
        t("missing_params_msg", "Missing parameters: {keys}", keys=", ".join(missing_keys))
    )

region = cfg.get("region", "ous" if cfg.get("ous", True) else "us")
low_threshold = cfg.get("low_threshold", 70)
high_threshold = cfg.get("high_threshold", 180)
unit = cfg.get("unit", "mg/dL")

try:
    dexcom = Dexcom(
        username=cfg["username"],
        password=cfg["password"],
        region=region
    )
    reading = dexcom.get_current_glucose_reading() or dexcom.get_latest_glucose_reading()
except Exception as exc:
    print_genmon(
        t("connection_error_title", "-- ⚠️"),
        t("connection_error_msg", "Connection error: {error}", error=str(exc))
    )

if not reading:
    print_genmon(
        t("no_reading_title", "-- ⚠️"),
        t("no_reading_msg", "No glucose value available.")
    )

try:
    if unit.lower() == "mmol/l":
        val_str = f"{reading.mmol_l:.1f}"
        display_unit = "mmol/L"
    else:
        val_str = f"{reading.value}"
        display_unit = "mg/dL"

    arrow = reading.trend_arrow or ""
    raw_txt = html.escape(f"{val_str} {arrow}".strip())

    if reading.value < low_threshold or reading.value > high_threshold:
        txt = f'<span foreground="{ALERT_COLOR}" weight="bold">{raw_txt}</span>'
    else:
        txt = f'<span foreground="{TARGET_COLOR}">{raw_txt}</span>'

    reading_dt = reading.datetime
    if reading_dt.tzinfo is not None:
        now = datetime.now(reading_dt.tzinfo)
        local_dt = reading_dt.astimezone()
    else:
        now = datetime.now()
        local_dt = reading_dt

    diff_minutes = max(0, int((now - reading_dt).total_seconds() // 60))
    time_str = local_dt.strftime("%H:%M")
    trend_desc = reading.trend_description or t("unknown_trend", "Unknown")

    tool_text = t(
        "tooltip",
        "Glucose: {value} {unit} ({trend})\nTime: {time} ({minutes} min ago)",
        value=val_str,
        unit=display_unit,
        trend=trend_desc,
        time=time_str,
        minutes=diff_minutes
    )

    print_genmon(txt, html.escape(tool_text))

except Exception as exc:
    print_genmon(
        t("format_error_title", "Dexcom: Format error"),
        t("format_error_msg", "Error processing data: {error}", error=str(exc))
    )