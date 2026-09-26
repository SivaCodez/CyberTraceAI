import streamlit as st
import streamlit.components.v1 as components
import os

# Import your working pipeline modules
from input import process_investigation_data
from standerdise import standardize_data
from network import build_network
from visualize import generate_html_graph

# Configure the Streamlit page
st.set_page_config(page_title="CyberTrace AI", layout="wide", initial_sidebar_state="expanded")

# App Header
st.title("CyberTrace AI")
st.markdown("### AI-Powered Criminal Network Analysis System")

# Sidebar for controls
st.sidebar.header("Investigation Controls")
csv_file = st.sidebar.text_input("Structured Data (CSV)", value="crime1.csv")
txt_file = st.sidebar.text_input("Unstructured Reports (TXT)", value="crime.txt")

# Button to trigger the pipeline
if st.sidebar.button("Generate Network Graph"):
    
    with st.spinner("Processing data and building network..."):
        # 1. Extract raw data
        raw_df = process_investigation_data(csv_file, txt_file)
        
        # 2. Standardize relationships and clean data
        clean_df = standardize_data(raw_df)
        
        # 3. Build the NetworkX graph and calculate roles
        graph = build_network(clean_df)
        
        # 4. Generate the PyVis HTML visualization
        html_file = generate_html_graph(graph, output_file="network_graph.html")
        
    st.success("Analysis Complete!")
    
    # Render the Interactive Graph
    st.subheader("Interactive Criminal Network")
    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
            # Embed the HTML directly into the Streamlit UI
            components.html(source_code, height=820, scrolling=False)
            
    # Display the raw standardized data table below the graph
    st.subheader("Standardized Data Records")
    if not clean_df.empty:
        # Hide the Date column for the UI display if it exists
        display_df = clean_df.drop(columns=['Date']) if 'Date' in clean_df.columns else clean_df
        st.dataframe(display_df, use_container_width=True)
    else:
        st.warning("No connections were extracted from the provided files.")