import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import pandas as pd
import os

from input import process_investigation_data

# 1. Set Wide Layout
st.set_page_config(layout="wide", page_title="CyberTrace AI", initial_sidebar_state="expanded")

# 2. Custom CSS for true-black background and layout padding
st.markdown("""
    <style>
           .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
            }
           /* Make the main app background extremely dark/black */
           .stApp {
               background-color: #050505;
           }
           /* Style the sidebar slightly lighter for contrast */
           [data-testid="stSidebar"] {
               background-color: #111111;
           }
    </style>
    """, unsafe_allow_html=True)

# 3. Main Header (Top Left, always visible, single line)
st.markdown("""
    <h1 style='text-align: left; font-size: 2.5em; font-weight: 900; margin-bottom: 10px; margin-top: 0px;'>
        <span style='color: #00E6CC;'>Cyber</span><span style='color: #FF3366;'>Trace</span> <span style='color: #FFFFFF;'>AI</span>
    </h1>
    <hr style='border: 1px solid #333; margin-top: 0px; margin-bottom: 25px;'>
""", unsafe_allow_html=True)

# 4. Sidebar: Navigation & Data Upload
st.sidebar.header("🧭 Navigation")
page = st.sidebar.radio("Select View:", ["Interactive Dashboard", "Raw Data Details"])

st.sidebar.markdown("---")
st.sidebar.header("📁 Data Sources")

csv_file = st.sidebar.file_uploader("Upload Structured Data (CSV)", type=["csv"])
txt_file = st.sidebar.file_uploader("Upload Unstructured Reports (TXT)", type=["txt"])
analyze_btn = st.sidebar.button("Generate Network", type="primary", use_container_width=True)

# 5. Handle Data Processing and Session State
# Using session_state ensures data persists when switching between the Dashboard and Data Details views
if analyze_btn:
    if csv_file is None and txt_file is None:
        st.sidebar.warning("Please upload at least one file (CSV or TXT).")
    else:
        with st.spinner("Extracting entities and building network..."):
            csv_path = "temp_data.csv"
            txt_path = "temp_report.txt"
            
            if csv_file:
                with open(csv_path, "wb") as f:
                    f.write(csv_file.getbuffer())
            if txt_file:
                with open(txt_path, "wb") as f:
                    f.write(txt_file.getbuffer())
                    
            # Store the resulting dataframe in Streamlit's session memory
            st.session_state['network_data'] = process_investigation_data(
                csv_path if csv_file else "missing.csv", 
                txt_path if txt_file else "missing.txt"
            )

# 6. Page Routing
if 'network_data' in st.session_state:
    df = st.session_state['network_data']

    if page == "Interactive Dashboard":
        col1, col2 = st.columns([3, 1]) 
        
        with col1:
            if not df.empty:
                G = nx.Graph()
                
                for index, row in df.iterrows():
                    source = str(row.get('Suspect', 'Unknown')).strip()
                    target = str(row.get('Target', 'Unknown')).strip()
                    relation = str(row.get('Relationship', 'Unknown')).strip()
                    
                    if source not in ["Unknown", "None", ""] and target not in ["Unknown", "None", ""]:
                        # Add Suspect Node (Neon Pink/Red)
                        G.add_node(source, title=source, label=source, color="#FF3366")
                        # Add Target Node (Neon Cyan)
                        G.add_node(target, title=target, label=target, color="#00E6CC")
                        # Add Edge
                        G.add_edge(source, target, label=relation)
                
                # Match PyVis background to the true black Streamlit background
                net = Network(height="700px", width="100%", bgcolor="#050505", font_color="white", directed=True)
                net.from_nx(G)
                
                # Graph styling: Massive physics adjustments for wider node spacing
                net.set_options("""
                var options = {
                  "nodes": {
                    "shape": "ellipse",
                    "font": { 
                        "size": 28, 
                        "color": "#FFFFFF", 
                        "face": "Arial",
                        "bold": true
                    },
                    "margin": 15,
                    "borderWidth": 2,
                    "shadow": true
                  },
                  "edges": {
                    "font": { 
                        "size": 18, 
                        "align": "middle", 
                        "color": "#00E6CC", 
                        "background": "rgba(5, 5, 5, 0.8)",
                        "strokeWidth": 0
                    },
                    "color": { "inherit": false, "color": "#4A5568" },
                    "smooth": { "type": "continuous" },
                    "width": 2
                  },
                  "physics": {
                    "barnesHut": { 
                        "gravitationalConstant": -80000, 
                        "centralGravity": 0.1, 
                        "springLength": 500,
                        "springConstant": 0.02
                    }
                  }
                }
                """)
                
                path = "network_graph.html"
                net.save_graph(path)
                
                HtmlFile = open(path, 'r', encoding='utf-8')
                components.html(HtmlFile.read(), height=720, scrolling=False)
            else:
                st.error("No valid connections were extracted. Check your file format.")

        with col2:
            st.markdown("### 📊 Network Stats")
            if not df.empty:
                st.metric("Total Connections Found", len(df))
                unique_entities = set(df['Suspect'].dropna()).union(set(df['Target'].dropna()))
                unique_entities = {e for e in unique_entities if e not in ["Unknown", "None", None, ""]}
                st.metric("Unique Entities Tracked", len(unique_entities))
                
                st.divider()
                st.markdown("### 🎯 Top Suspects")
                top_suspects = df[~df['Suspect'].isin(['None', 'Unknown', ''])].copy()
                st.dataframe(top_suspects['Suspect'].value_counts().head(5), use_container_width=True)

    elif page == "Raw Data Details":
        st.subheader("🗄️ Extracted Investigation Data")
        st.markdown("Review the structured connections extracted via Pandas and spaCy.")
        st.dataframe(df, use_container_width=True, height=600)

else:
    st.info("👈 Upload your data files in the sidebar and click Generate to start the analysis.")