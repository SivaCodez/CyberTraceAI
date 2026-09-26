from input import process_investigation_data
from standerdise import standardize_data
from network import build_network
from visualize import generate_html_graph
import os
import webbrowser

def main():
    csv_file = "crime1.csv"
    txt_file = "crime.txt"
    
    print(f"\n[Step 1] Extracting raw data from {csv_file} and {txt_file}...")
    raw_df = process_investigation_data(csv_file, txt_file)
    
    print("[Step 2] Standardizing dates and relationships...")
    clean_df = standardize_data(raw_df)
    
    print("[Step 3] Building the NetworkX graph and analyzing roles...")
    graph = build_network(clean_df)
    
    print("[Step 4] Generating interactive PyVis HTML graph...")
    # This will create network_graph.html in your current folder
    html_file = generate_html_graph(graph, output_file="network_graph.html")
    
    print("\n--- PROCESS COMPLETE ---")
    print(f"Network visualization successfully saved to: {html_file}")
    
    # Optional: Automatically open the generated HTML file in your default web browser
    file_path = f"file://{os.path.abspath(html_file)}"
    webbrowser.open(file_path)

if __name__ == "__main__":
    main()