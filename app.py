import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import pandas as pd
import os

from input import process_investigation_data

# 1. Set Wide Layout
st.set_page_config(layout="wide", page_title="CyberTrace AI", initial_sidebar_state="expanded")

# 2. Custom CSS for layout padding
st.markdown("""
    <style>
           .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
            }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar: Big Stylized CyberTrace AI Header
st.sidebar.markdown("""
    <h1 style='text-align: left; font-size: 2.8em; font-weight: 900; margin-bottom: 0px; line-height: 1.1;'>
        <span style='color: #00E6CC;'>Cyber</span><span style='color: #FF3366;'>Trace</span> <br>AI
    </h1>
    <hr style='margin-top: 10px; margin-bottom: 20px; border-color: #333;'>
""", unsafe_allow_html=True)

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
            csv_path = "temp_data.csv"
            txt_path = "temp_report.txt"
            
            if csv_file:
                with open(csv_path, "wb") as f:
                    f.write(csv_file.getbuffer())
            if txt_file:
                with open(txt_path, "wb") as f:
                    f.write(txt_file.getbuffer())
                    
            df = process_investigation_data(
                csv_path if csv_file else "missing.csv", 
                txt_path if txt_file else "missing.txt"
            )
            
        with tab1:
            col1, col2 = st.columns([3, 1]) 
            
            with col1:
                st.subheader("Interactive Criminal Network")
                
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
                    
                    net = Network(height="650px", width="100%", bgcolor="#0E1117", font_color="white", directed=True)
                    net.from_nx(G)
                    
                    # Graph styling: Ellipse shapes (text inside), big fonts, glowing shadows
                    net.set_options("""
                    var options = {
                      "nodes": {
                        "shape": "ellipse",
                        "font": { 
                            "size": 24, 
                            "color": "#FFFFFF", 
                            "face": "Arial",
                            "bold": true
                        },
                        "margin": 12,
                        "borderWidth": 2,
                        "shadow": true
                      },
                      "edges": {
                        "font": { 
                            "size": 18, 
                            "align": "middle", 
                            "color": "#00E6CC", 
                            "background": "rgba(14, 17, 23, 0.7)",
                            "strokeWidth": 0
                        },
                        "color": { "inherit": false, "color": "#5C6B82" },
                        "smooth": { "type": "continuous" },
                        "width": 2
                      },
                      "physics": {
                        "barnesHut": { "gravitationalConstant": -40000, "centralGravity": 0.4, "springLength": 300 }
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
                st.subheader("Network Statistics")
                if not df.empty:
                    st.metric("Total Connections Found", len(df))
                    unique_entities = set(df['Suspect'].dropna()).union(set(df['Target'].dropna()))
                    unique_entities = {e for e in unique_entities if e not in ["Unknown", "None", None, ""]}
                    st.metric("Unique Entities Tracked", len(unique_entities))
                    
                    st.divider()
                    st.markdown("### Top Suspects")
                    st.caption("Individuals initiating the most connections:")
                    top_suspects = df[~df['Suspect'].isin(['None', 'Unknown', ''])].copy()
                    st.dataframe(top_suspects['Suspect'].value_counts().head(5), use_container_width=True)

        with tab2:
            st.subheader("Extracted Investigation Data")
            st.dataframe(df, use_container_width=True)

else:
    st.info("👈 Upload your data files in the sidebar and click Generate to start the analysis.")