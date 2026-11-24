import re

import pandas as pd


IP_PATTERN = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")
SPECIAL_CHARS = ("@", "-", "?", "_", "=", "%", "&")
SUSPICIOUS_KEYWORDS = (
    "login",
    "verify",
    "update",
    "secure",
    "bank",
    "confirm",
    "account",
    "password",
)


def classify_phishing(label):
    label_lower = str(label).lower().strip()
    if label_lower in ("phishing", "malicious"):
        return 1
    if label_lower in ("benign", "legitimate"):
        return 0
    return None


def has_ip_address(url):
    return int(IP_PATTERN.search(str(url)) is not None)


def count_special_chars(url):
    url = str(url)
    return sum(url.count(char) for char in SPECIAL_CHARS)


def has_suspicious_keyword(url):
    url = str(url).lower()
    return int(any(keyword in url for keyword in SUSPICIOUS_KEYWORDS))


def transform_dataset(df_raw):
    """Clean raw records and derive phishing and URL features."""
    df = df_raw.copy()

    df = df.dropna(subset=["URL", "label", "Domain"])
    df = df[df["URL"].astype(str).str.strip() != ""]
    df = df[df["Domain"].astype(str).str.strip() != ""]
    df = df[df["label"].astype(str).str.strip() != ""]
    df = df.reset_index(drop=True)

    df["is_phishing"] = df["label"].apply(classify_phishing)
    df = df.dropna(subset=["is_phishing"])
    df["is_phishing"] = df["is_phishing"].astype(int)

    df["has_ip"] = df["URL"].apply(has_ip_address).astype(int)
    df["special_char_count"] = df["URL"].apply(count_special_chars).astype(int)
    df["has_suspicious_keyword"] = df["URL"].apply(has_suspicious_keyword).astype(int)

    numeric_columns = [
        "length",
        "has_ip",
        "special_char_count",
        "has_suspicious_keyword",
        "is_phishing",
    ]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce").astype(int)

    return df
