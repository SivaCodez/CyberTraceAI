import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import pandas as pd

# 1. Set Wide Layout (Must be the first Streamlit command)
st.set_page_config(layout="wide", page_title="Criminal Network Analysis", initial_sidebar_state="expanded")

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
st.sidebar.markdown("## INNOVEXA X")
st.sidebar.markdown("**Team ID:** 142945")
st.sidebar.markdown("**Leader:** Sivahari Ratheesh")
st.sidebar.markdown("---")
st.sidebar.header("📁 Data Sources")

csv_file = st.sidebar.file_uploader("Upload Structured Data (CSV)", type=["csv"])
txt_file = st.sidebar.file_uploader("Upload Unstructured Reports (TXT)", type=["txt"])
analyze_btn = st.sidebar.button("Generate Network & Insights", type="primary", use_container_width=True)

# 4. Main UI: Navigation Tabs to prevent scrolling
tab1, tab2 = st.tabs(["🔎 Investigation Dashboard", "🗄️ Raw Data Records"])

if analyze_btn:
    
    # [YOUR DATA PROCESSING CODE GOES HERE]
    # Example: clean_df = standardize_data(process_investigation_data("temp.csv", "temp.txt"))
    
    # 5. Dashboard Tab: Side-by-Side Layout
    with tab1:
        # Create two columns: 70% width for the Graph, 30% for AI Insights
        col1, col2 = st.columns([2.5, 1]) 
        
        with col1:
            st.subheader("Interactive Criminal Network")
            
            # Build Graph
            G = nx.Graph()
            # Loop through your clean_df here to add nodes/edges...
            # Example: G.add_node("Rahul", size=25) 
            
            # PyVis configuration for larger text and better visuals
            net = Network(height="650px", width="100%", bgcolor="#0E1117", font_color="white", directed=True)
            net.from_nx(G)
            
            # Inject options to increase font size and fix physics
            net.set_options("""
            var options = {
              "nodes": {
                "font": {
                  "size": 22,
                  "color": "#FFFFFF",
                  "face": "Arial"
                },
                "shape": "dot"
              },
              "edges": {
                "font": {
                  "size": 16,
                  "align": "middle",
                  "color": "#A0AEC0",
                  "background": "none"
                },
                "color": {
                  "inherit": false,
                  "color": "#4A5568"
                },
                "smooth": {
                  "type": "continuous"
                }
              },
              "physics": {
                "barnesHut": {
                  "gravitationalConstant": -30000,
                  "centralGravity": 0.3,
                  "springLength": 250
                }
              }
            }
            """)
            
            path = "network_graph.html"
            net.save_graph(path)
            
            HtmlFile = open(path, 'r', encoding='utf-8')
            # Render graph flush with the container
            components.html(HtmlFile.read(), height=670, scrolling=False)

        with col2:
            st.subheader("AI Insights")
            st.info("🔴 **HIGH RISK**\n* **Rahul** (15 Connections)\n* Frequent suspicious transfers.")
            st.warning("🟠 **MEDIUM RISK**\n* **Anil** (7 Connections)")
            st.divider()
            st.markdown("### 🤖 Investigation Summary")
            st.write("Rahul is the most central figure, connecting directly to 4 known locations and initiating 11 transfers within the network.")
            # [YOUR GEMINI API CALL GOES HERE]

    # 6. Data Tab: Clean Database view 
    with tab2:
        st.subheader("Standardized Investigation Data")
        # st.dataframe(clean_df, use_container_width=True)
        st.write("Display your pandas dataframe here.")

else:
    st.info("👈 Upload your data files in the sidebar and click Generate to start the analysis.")