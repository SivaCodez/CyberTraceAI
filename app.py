import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import pandas as pd
import os

# Import your data processing function from your existing input.py file
from input import process_investigation_data

# 1. Set Wide Layout
st.set_page_config(layout="wide", page_title="CyberTrace AI", initial_sidebar_state="expanded")

# 2. Custom CSS to eliminate top white space
st.markdown("""
    <style>
           .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
            }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar: Team Info & Data Upload
st.sidebar.markdown("## CyberTrace AI")
st.sidebar.markdown("---")
st.sidebar.header("📁 Data Sources")

csv_file = st.sidebar.file_uploader("Upload Structured Data (CSV)", type=["csv"])
txt_file = st.sidebar.file_uploader("Upload Unstructured Reports (TXT)", type=["txt"])
analyze_btn = st.sidebar.button("Generate Network", type="primary", use_container_width=True)

# 4. Main UI: Navigation Tabs
tab1, tab2 = st.tabs(["🔎 Investigation Dashboard", "🗄️ Raw Data Records"])

if analyze_btn:
    if csv_file is None and txt_file is None:
        st.warning("Please upload at least one file (CSV or TXT) before generating.")
    else:
        with st.spinner("Extracting entities and building network..."):
            
            # --- FILE HANDLING FIX ---
            # Streamlit keeps uploads in memory. We must save them locally so input.py can read them.
            csv_path = "temp_data.csv"
            txt_path = "temp_report.txt"
            
            if csv_file:
                with open(csv_path, "wb") as f:
                    f.write(csv_file.getbuffer())
            if txt_file:
                with open(txt_path, "wb") as f:
                    f.write(txt_file.getbuffer())
                    
            # Run your extraction pipeline
            df = process_investigation_data(
                csv_path if csv_file else "missing.csv", 
                txt_path if txt_file else "missing.txt"
            )
            
        with tab1:
            col1, col2 = st.columns([3, 1]) 
            
            with col1:
                st.subheader("Interactive Criminal Network")
                
                if not df.empty:
                    # --- GRAPH BUILDING FIX ---
                    G = nx.Graph()
                    
                    # Loop through the extracted dataframe and add actual nodes/edges
                    for index, row in df.iterrows():
                        source = str(row.get('Suspect', 'Unknown'))
                        target = str(row.get('Target', 'Unknown'))
                        relation = str(row.get('Relationship', 'Unknown'))
                        
                        if source != "Unknown" and target != "Unknown" and source != "None" and target != "None":
                            G.add_node(source, title=source, size=20)
                            G.add_node(target, title=target, size=20)
                            G.add_edge(source, target, label=relation)
                    
                    # Configure PyVis
                    net = Network(height="650px", width="100%", bgcolor="#0E1117", font_color="white", directed=True)
                    net.from_nx(G)
                    
                    net.set_options("""
                    var options = {
                      "nodes": {
                        "font": { "size": 22, "color": "#FFFFFF", "face": "Arial" },
                        "shape": "dot"
                      },
                      "edges": {
                        "font": { "size": 16, "align": "middle", "color": "#A0AEC0", "background": "none" },
                        "color": { "inherit": false, "color": "#4A5568" },
                        "smooth": { "type": "continuous" }
                      },
                      "physics": {
                        "barnesHut": { "gravitationalConstant": -30000, "centralGravity": 0.3, "springLength": 250 }
                      }
                    }
                    """)
                    
                    path = "network_graph.html"
                    net.save_graph(path)
                    
                    HtmlFile = open(path, 'r', encoding='utf-8')
                    components.html(HtmlFile.read(), height=670, scrolling=False)
                else:
                    st.error("No valid connections were extracted. Check your file format.")

            with col2:
                # Replaced AI Insights with functional Network Statistics
                st.subheader("Network Statistics")
                if not df.empty:
                    st.metric("Total Connections Found", len(df))
                    unique_entities = set(df['Suspect'].dropna()).union(set(df['Target'].dropna()))
                    # Clean out "None" or "Unknown" from the count
                    unique_entities = {e for e in unique_entities if e not in ["Unknown", "None", None]}
                    st.metric("Unique Entities Tracked", len(unique_entities))
                    
                    st.divider()
                    st.markdown("### Top Suspects")
                    st.caption("Individuals initiating the most connections:")
                    # Count which suspects appear the most
                    top_suspects = df[df['Suspect'] != 'None']['Suspect'].value_counts().head(5)
                    st.dataframe(top_suspects, use_container_width=True)

        with tab2:
            st.subheader("Extracted Investigation Data")
            st.dataframe(df, use_container_width=True)

else:
    st.info("👈 Upload your data files in the sidebar and click Generate to start the analysis.")