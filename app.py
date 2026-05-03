import streamlit as st
import pandas as pd
from outscraper import ApiClient
import base64

# Page Configuration
st.set_page_config(page_title="Retail Health Tracker", layout="wide")
st.title("📍 Retail Opening & Closing Tracker")
st.markdown("""
Extract data from Google Maps to identify active and defunct businesses. 
*To track a 5-year trend, compare your current results with historical review dates.*
""")

# Sidebar for API Key & Settings
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Outscraper API Key", type="password", help="Get your key at outscraper.com")
search_type = st.sidebar.selectbox("Business Status to Find", ["Operational", "Closed Permanently", "Closed Temporarily"])

# Mapping status to API filters
status_map = {
    "Operational": "operational",
    "Closed Permanently": "closed_permanently",
    "Closed Temporarily": "closed_temporarily"
}

# Main UI
query = st.text_input("Enter Retail Area & Category", "Shops in Oxford Street, London")
limit = st.number_input("Results Limit", min_value=1, max_value=500, value=50)

if st.button("Run Tracker"):
    if not api_key:
        st.warning("Please enter your API Key in the sidebar.")
    else:
        client = ApiClient(api_key=api_key)
        with st.spinner(f"Searching for {search_type} businesses..."):
            try:
                # Execution
                results = client.google_maps_search(
                    [query],
                    limit=limit,
                    language='en',
                    # Applying the status filter via Outscraper's logic
                    filters={'business_status': ['=', status_map[search_type]]} 
                )
                
                # Processing Results
                df = pd.DataFrame(results[0])
                
                if not df.empty:
                    st.success(f"Found {len(df)} businesses.")
                    
                    # Displaying key data points
                    cols_to_show = ['name', 'site', 'subtypes', 'full_address', 'rating', 'reviews']
                    available_cols = [c for c in cols_to_show if c in df.columns]
                    st.dataframe(df[available_cols])
                    
                    # Download Link
                    csv = df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="retail_trend_{search_type}.csv">Download CSV File</a>'
                    st.markdown(href, unsafe_base_html=True)
                else:
                    st.info("No businesses found matching this status in the area.")
                    
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.caption("Pro Tip: To find 'New Openings' in the last year, sort your downloaded CSV by review count (low) or look for 'New' tags in the subtypes.")
