import streamlit as st
from src.valuation import parse_pasted_sigs, tally_site_values
from pathlib import Path
import base64

# Add background image to page
image_path = Path(__file__).parent / "bison.png"

st.write("Looking for image:", image_path)
st.write("Image exists:", image_path.exists())

image_data = base64.b64encode(image_path.read_bytes()).decode()

st.markdown(
    f"""
    <style>
    .stApp {{
        background: url("data:image/png;base64,{image_data}") center / cover fixed no-repeat;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("The Hole Buffalo")
sigs_paste = st.text_area("Paste sites here.", height=300)
submit_sigs = st.button("Submit Sigs")

if "site_list" not in st.session_state:
    st.session_state.site_list = None

if submit_sigs:
    sites = parse_pasted_sigs(sigs_paste).reset_index(drop=True)
    sites.insert(0, "_row_id", range(len(sites)))
    st.session_state.site_list = sites
    st.session_state.pop("sites_editor", None)

if st.session_state.site_list is not None:
    sites = st.session_state.site_list.copy()

    # Keep original values for calculations; display a scaled value in the table.
    display_sites = sites.copy()
    display_sites["Value (millions)"] = display_sites["Value"] / 1_000_000
    display_sites = display_sites.drop(columns="Value")

    edited = st.data_editor(
        display_sites,
        hide_index=True,
        num_rows="delete",
        disabled=["_row_id", "Signature Code", "Site Type", "Site Name",
                  "Value (millions)"],
        column_order=[
            "Signature Code",
            "Site Type",
            "Site Name",
            "Value (millions)",
        ],
        column_config={
            "_row_id": None,
            "Value (millions)": st.column_config.NumberColumn(
                "Value",
                format="%.1f million",
            ),
        },
        key="sites_editor",
    )

    # Keep only original rows whose IDs remain in the editor.
    remaining_ids = set(edited["_row_id"])
    sites = sites[sites["_row_id"].isin(remaining_ids)].reset_index(drop=True)
    st.session_state.site_list = sites

    total_value = tally_site_values(sites)
    st.write(f"Total Value: {total_value / 1_000_000_000:,.3f} billion")

    category_totals = (
        sites.groupby("Site Type")["Value"]
        .sum()
        .sort_values(ascending=False)
    )

    st.subheader("Value by Site Category")
    for category, value in category_totals.items():
        st.write(f"{category}: {value / 1_000_000_000:,.3f} billion")