
import streamlit as st
import requests
import pandas as pd
import time

GOOGLE_MAPS_ENGINE = "google_maps"
ADS_TRANSPARENCY_ENGINE = "google_ads_transparency"

# ---- STREAMLIT APP ----
st.title("Active Advertiser Finder via SERP API")

# API key input
SERPAPI_KEY = st.text_input("Enter your SERP API key", type="password")

query = st.text_input("Business type (e.g., landscaper)")
location = st.text_input("City (e.g., Pasadena, CA)")

# ---- FUNCTIONS ----
def fetch_google_maps_results(query, location):
    all_results = []
    start = 0
    while True:
        params = {
            "engine": GOOGLE_MAPS_ENGINE,
            "q": query,
            "location": location,
            "start": start,
            "api_key": SERPAPI_KEY
        }
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()

        results = data.get("local_results", [])
        if not results:
            break

        for result in results:
            if "website" in result:
                all_results.append({
                    "name": result.get("title"),
                    "website": result.get("website"),
                    "address": result.get("address", ""),
                    "phone": result.get("phone", "")
                })

        start += 20
        time.sleep(1)  # be respectful of rate limits

    return all_results

def check_ads_transparency(website):
    params = {
        "engine": ADS_TRANSPARENCY_ENGINE,
        "q": website,
        "api_key": SERPAPI_KEY
    }
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()

    ads = data.get("ads", [])
    for ad in ads:
        if ad.get("active_ads", 0) > 0:
            return True
    return False

if st.button("Find Advertising Businesses"):
    if not SERPAPI_KEY:
        st.error("Please enter your SERP API key.")
    elif not query or not location:
        st.warning("Please enter both a business type and a city.")
    else:
        st.info("Scraping Google Maps results...")
        results = fetch_google_maps_results(query, location)
        st.success(f"Found {len(results)} businesses with websites.")

        advertisers = []
        progress = st.progress(0)
        for i, biz in enumerate(results):
            if check_ads_transparency(biz["website"]):
                advertisers.append(biz)
            progress.progress((i + 1) / len(results))
            time.sleep(0.5)  # throttle to avoid detection

        if advertisers:
            df = pd.DataFrame(advertisers)
            st.dataframe(df)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV of Advertisers", data=csv, file_name="advertisers.csv", mime="text/csv")
        else:
            st.warning("No advertisers found among businesses with websites.")
