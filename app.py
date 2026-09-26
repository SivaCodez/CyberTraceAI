import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import pandas as pd
import os

from input import process_investigation_data

# 1. Set Wide Layout
st.set_page_config(layout="wide", page_title="CyberTrace AI", initial_sidebar_state="expanded")

# Initialize Session State for Page Navigation
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = "Interactive Dashboard"

# 2. Custom CSS
st.markdown("""
    <style>
           .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
            }
           .stApp {
               background-color: #050505;
           }
           [data-testid="stSidebar"] {
               background-color: #111111;
           }
           .ai-insight-box {
               background-color: #1a1c23;
               border-left: 4px solid #00E6CC;
               padding: 15px;
               border-radius: 5px;
               margin-bottom: 10px;
           }
           .ai-insight-box-leader {
               background-color: #1a1c23;
               border-left: 4px solid #FFD700;
               padding: 15px;
               border-radius: 5px;
               margin-bottom: 10px;
           }
    </style>
    """, unsafe_allow_html=True)

# 3. Main Header
st.markdown("""
    <h1 style='text-align: left; font-size: 2.5em; font-weight: 900; margin-bottom: 10px; margin-top: 0px;'>
        <span style='color: #00E6CC;'>Cyber</span><span style='color: #FF3366;'>Trace</span> <span style='color: #FFFFFF;'>AI</span>
    </h1>
    <hr style='border: 1px solid #333; margin-top: 0px; margin-bottom: 25px;'>
""", unsafe_allow_html=True)

# 4. Sidebar: Navigation
st.sidebar.header("Navigation")

if st.sidebar.button("Interactive Dashboard", use_container_width=True):
    st.session_state['current_page'] = "Interactive Dashboard"
    
if st.sidebar.button("Raw Data Details", use_container_width=True):
    st.session_state['current_page'] = "Raw Data Details"

st.sidebar.markdown("---")
st.sidebar.header("📁 Data Sources")

csv_file = st.sidebar.file_uploader("Upload Structured Data (CSV)", type=["csv"])
txt_file = st.sidebar.file_uploader("Upload Unstructured Reports (TXT)", type=["txt"])
analyze_btn = st.sidebar.button("Generate Network", type="primary", use_container_width=True)

# 5. Handle Data Processing
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
                    
            st.session_state['network_data'] = process_investigation_data(
                csv_path if csv_file else "missing.csv", 
                txt_path if txt_file else "missing.txt"
            )
            st.session_state['current_page'] = "Interactive Dashboard" 

# 6. Page Routing
if 'network_data' in st.session_state:
    df = st.session_state['network_data']

    if st.session_state['current_page'] == "Interactive Dashboard":
        col1, col2 = st.columns([3, 1]) 
        
        with col1:
            if not df.empty:
                G = nx.Graph()
                
                # Create a list of all identified "Suspects" to help with coloring later
                suspects_set = set(df['Suspect'].dropna().astype(str).str.strip())
                
                # Step 1: Build edges
                for index, row in df.iterrows():
                    source = str(row.get('Suspect', 'Unknown')).strip()
                    target = str(row.get('Target', 'Unknown')).strip()
                    relation = str(row.get('Relationship', 'Unknown')).strip()
                    
                    if source not in ["Unknown", "None", ""] and target not in ["Unknown", "None", ""]:
                        G.add_edge(source, target, label=relation)
                
                # Step 2: Calculate distinct network math
                if len(G.nodes) > 0:
                    degrees = dict(G.degree())
                    # Use Betweenness for the Leader (who acts as a bridge between groups)
                    centrality = nx.betweenness_centrality(G) 
                    
                    leader_node = max(centrality, key=centrality.get)
                    most_connected_node = max(degrees, key=degrees.get)
                else:
                    degrees = {}
                    centrality = {}
                    leader_node = None
                    most_connected_node = None

                # Step 3: Apply STRICT colors and tooltips
                for node in G.nodes():
                    conns = degrees.get(node, 0)
                    score = round(centrality.get(node, 0), 4) # Showing 4 decimals for precision
                    
                    hover_text = f"{node}\nConnections: {conns}\nCentrality Score: {score}"
                    
                    # Strictly define colors
                    if node == leader_node:
                        node_color = "#FFD700"  # Yellow for Leader ONLY
                    elif node in suspects_set:
                        node_color = "#FF3366"  # Pink for normal Suspects
                    else:
                        node_color = "#00E6CC"  # Cyan for Targets/Locations
                    
                    G.nodes[node]['title'] = hover_text
                    G.nodes[node]['label'] = node
                    G.nodes[node]['color'] = node_color
                
                net = Network(height="700px", width="100%", bgcolor="#050505", font_color="white", directed=True)
                net.from_nx(G)
                
                net.set_options("""
                var options = {
                  "nodes": {
                    "shape": "ellipse",
                    "font": { "size": 32, "color": "#FFFFFF", "face": "Arial", "bold": true },
                    "margin": 24,
                    "borderWidth": 3,
                    "shadow": true
                  },
                  "edges": {
                    "font": { "size": 18, "align": "middle", "color": "#00E6CC", "background": "rgba(5, 5, 5, 0.8)", "strokeWidth": 0 },
                    "color": { "inherit": false, "color": "#4A5568" },
                    "smooth": { "type": "continuous" },
                    "width": 3
                  },
                  "physics": {
                    "barnesHut": { "gravitationalConstant": -20000, "centralGravity": 0.4, "springLength": 250, "springConstant": 0.04 },
                    "minVelocity": 0.75
                  },
                  "interaction": { "hover": true, "tooltipDelay": 200 }
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
                
                st.divider()
                st.markdown("### 🤖 AI Insights")
                if leader_node:
                    st.markdown(f"""
                        <div class="ai-insight-box-leader">
                            <span style="color: #FFD700; font-weight: bold;">👑 Suspected Kingpin:</span><br>
                            <b>{leader_node}</b> has the highest centrality score, acting as the primary bridge holding this network together.
                        </div>
                    """, unsafe_allow_html=True)
                
                if most_connected_node:
                    st.markdown(f"""
                        <div class="ai-insight-box">
                            <span style="color: #00E6CC; font-weight: bold;">📡 Top Distributor:</span><br>
                            <b>{most_connected_node}</b> has the highest volume of direct interactions ({degrees.get(most_connected_node, 0)} connections).
                        </div>
                    """, unsafe_allow_html=True)

    elif st.session_state['current_page'] == "Raw Data Details":
        st.subheader("🗄️ Extracted Investigation Data")
        st.markdown("Review the structured connections extracted via Pandas and spaCy.")
        
        def style_relationships(val):
            val_str = str(val).upper()
            if 'CALLED' in val_str or 'COMMUNICATED' in val_str:
                return 'color: #FF3366; font-weight: bold;'
            elif 'TRANSFERRED' in val_str or 'MONEY' in val_str:
                return 'color: #00E6CC; font-weight: bold;'
            elif 'LOCATED' in val_str or 'VISITED' in val_str:
                return 'color: #FFD700; font-weight: bold;'
            return 'color: #A0AEC0;'

        try:
            styled_df = df.style.map(style_relationships, subset=['Relationship'])
        except AttributeError:
            styled_df = df.style.applymap(style_relationships, subset=['Relationship'])
            
        st.dataframe(styled_df, use_container_width=True, height=600, hide_index=True)

else:
    st.info("👈 Upload your data files in the sidebar and click Generate to start the analysis.")