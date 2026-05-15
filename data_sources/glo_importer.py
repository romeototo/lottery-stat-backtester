from __future__ import annotations

from pathlib import Path
from typing import BinaryIO
import re

import pandas as pd

from analyzer import prepare_dataframe


SCHEMA_COLUMNS = [
    "date",
    "first_prize",
    "last_2_digits",
    "front_3_1",
    "front_3_2",
    "last_3_1",
    "last_3_2",
    "source",
]

COLUMN_ALIASES = {
    "date": {
        "date",
        "draw_date",
        "drawdate",
        "draw_dt",
        "lottery_date",
        "lotterydate",
        "period_date",
        "perioddate",
        "draw",
        "period",
        "งวดวันที่",
        "วันที่",
        "วันที่ออกรางวัล",
        "วันที่ออกรางวัลงวด",
        "วันออกสลาก",
        "งวด",
    },
    "first_prize": {
        "first_prize",
        "firstprize",
        "first_prize_number",
        "firstprizenumber",
        "prize1",
        "reward1",
        "winning_number",
        "winningnumber",
        "รางวัลที่1",
        "รางวัลที่ 1",
        "เลขรางวัลที่1",
        "เลขรางวัลที่ 1",
        "รางวัลที่หนึ่ง",
        "first",
    },
    "last_2_digits": {
        "last_2_digits",
        "last2",
        "2digits",
        "last_2",
        "last2digits",
        "two_digit",
        "twodigit",
        "two_digits",
        "twodigits",
        "last_two_digits",
        "lasttwodigits",
        "เลขท้าย2ตัว",
        "เลขท้าย 2 ตัว",
        "รางวัลเลขท้าย2ตัว",
        "รางวัลเลขท้าย 2 ตัว",
        "เลขท้ายสองตัว",
    },
    "front_3_1": {
        "front_3_1",
        "front3_1",
        "front_3_first",
        "front3first",
        "front_three_1",
        "frontthree1",
        "เลขหน้า3ตัว_1",
        "เลขหน้า 3 ตัว 1",
        "รางวัลเลขหน้า3ตัว1",
        "รางวัลเลขหน้า 3 ตัว ครั้งที่ 1",
    },
    "front_3_2": {
        "front_3_2",
        "front3_2",
        "front_3_second",
        "front3second",
        "front_three_2",
        "frontthree2",
        "เลขหน้า3ตัว_2",
        "เลขหน้า 3 ตัว 2",
        "รางวัลเลขหน้า3ตัว2",
        "รางวัลเลขหน้า 3 ตัว ครั้งที่ 2",
    },
    "last_3_1": {
        "last_3_1",
        "last3_1",
        "back_3_1",
        "back3_1",
        "last_3_first",
        "last3first",
        "last_three_1",
        "lastthree1",
        "เลขท้าย3ตัว_1",
        "เลขท้าย 3 ตัว 1",
        "รางวัลเลขท้าย3ตัว1",
        "รางวัลเลขท้าย 3 ตัว ครั้งที่ 1",
    },
    "last_3_2": {
        "last_3_2",
        "last3_2",
        "back_3_2",
        "back3_2",
        "last_3_second",
        "last3second",
        "last_three_2",
        "lastthree2",
        "เลขท้าย3ตัว_2",
        "เลขท้าย 3 ตัว 2",
        "รางวัลเลขท้าย3ตัว2",
        "รางวัลเลขท้าย 3 ตัว ครั้งที่ 2",
    },
    "source": {
        "source",
        "แหล่งที่มา",
    },
}


def _clean_column_name(value: str) -> str:
    return re.sub(r"[\s\-_./()]+", "", str(value).strip().lower())


def _normalize_digit_text(value, width: int) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return ""
    if len(digits) > width:
        return text
    return digits.zfill(width)


def _normalize_date_text(value) -> str:
    if pd.isna(value):
        return ""
    parsed = pd.to_datetime(value, errors="coerce", format="mixed", dayfirst=False)
    if pd.isna(parsed):
        parsed = pd.to_datetime(value, errors="coerce", format="mixed", dayfirst=True)
    return "" if pd.isna(parsed) else parsed.date().isoformat()


def _read_table(file: str | Path | BinaryIO) -> pd.DataFrame:
    name = str(getattr(file, "name", file)).lower()
    if name.endswith(".csv"):
        return pd.read_csv(file, dtype=str)
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(file, dtype=str)
    raise ValueError("รองรับเฉพาะ CSV / Excel จาก GLO Open Data")


def normalize_glo_dataframe(raw_df: pd.DataFrame, default_source: str = "GLO Open Data official") -> pd.DataFrame:
    raw_df = raw_df.copy()
    normalized_lookup = {_clean_column_name(col): col for col in raw_df.columns}
    mapped = pd.DataFrame()

    for target, aliases in COLUMN_ALIASES.items():
        source_column = None
        for alias in aliases:
            candidate = _clean_column_name(alias)
            if candidate in normalized_lookup:
                source_column = normalized_lookup[candidate]
                break
        mapped[target] = raw_df[source_column] if source_column is not None else ""

    mapped["date"] = mapped["date"].map(_normalize_date_text)
    mapped["first_prize"] = mapped["first_prize"].map(lambda value: _normalize_digit_text(value, 6))
    mapped["last_2_digits"] = mapped["last_2_digits"].map(lambda value: _normalize_digit_text(value, 2))
    for column in ["front_3_1", "front_3_2", "last_3_1", "last_3_2"]:
        mapped[column] = mapped[column].map(lambda value: _normalize_digit_text(value, 3))
    mapped["source"] = "official_glo"
    return prepare_dataframe(mapped[SCHEMA_COLUMNS])


def load_glo_file(file: str | Path | BinaryIO) -> pd.DataFrame:
    return normalize_glo_dataframe(_read_table(file))
