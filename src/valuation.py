import re
import json
import pandas as pd
import streamlit as st
from pathlib import Path

SITE_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sites.json"

def parse_pasted_sigs(pasted_sigs, site_data_path=SITE_DATA_PATH):
    rows = []

    for line in pasted_sigs.splitlines():
        match = re.match(
            r"^\s*(\S+)\s+(Ore|Wormhole|Combat|Data|Relic|Gas)\s+"
            r"\S+\s+(.+?)\s+\d+\s*[mh]\s+ago\s*$",
            line,
            re.IGNORECASE,
        )

        if match:
            rows.append({
                "Signature Code": match.group(1),
                "Site Type": match.group(2),
                "Site Name": match.group(3).strip(),
            })

    df = pd.DataFrame(rows)
    if not Path(site_data_path).exists():
        raise FileNotFoundError(
            f"Looking for site data at: {Path(site_data_path).resolve()}"
        )
    with open(site_data_path, "r", encoding="utf-8") as file:
        sites = json.load(file)

    value_by_name = {
        site["Site Name"].strip().casefold(): site["Value"]
        for site in sites
    }

    df["Value"] = df["Site Name"].str.casefold().map(value_by_name)
    df = df.dropna(subset=["Value"]).reset_index(drop=True)
    return df

def tally_site_values(site_list):
    return site_list["Value"].sum()