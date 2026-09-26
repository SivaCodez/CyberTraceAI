import networkx as nx
import pandas as pd

def build_network(df):
    """
    Builds a NetworkX graph and calculates roles.
    Uses Eigenvector Centrality to find true Leaders (influence-based),
    while keeping Degree Centrality for Foot Workers.
    """
    G = nx.DiGraph()
    
    if 'Date' in df.columns:
        df = df.drop(columns=['Date'])
        
    if df.empty:
        return G
        
    # 1. Add edges and nodes
    for _, row in df.iterrows():
        suspect = row['Suspect']
        target = row['Target']
        relationship = row['Relationship']
        
        G.add_edge(suspect, target, label=relationship, title=relationship)
        
    # 2. Analyze the network
    # We use the undirected version of the graph for Eigenvector math so 
    # one-way actions (like transferring money) don't break the influence flow.
    try:
        influence_scores = nx.eigenvector_centrality(G.to_undirected(), max_iter=1000)
    except:
        # Safe fallback if the graph is too small or disjointed
        influence_scores = nx.degree_centrality(G)
        
    degrees = dict(G.degree())
    
    if influence_scores:
        max_influence = max(influence_scores.values())
    else:
        max_influence = 0
        
    # 3. Assign roles based on the new logic
    for node in G.nodes():
        node_influence = influence_scores.get(node, 0)
        node_degree = degrees.get(node, 0)
        
        # Leader is the node with the highest influence score
        if node_influence == max_influence and node_degree > 0:
            role = "Leader / Kingpin"
            color = "#FF4B4B"  # Red
            size = 35
        # Foot workers are isolated to the edge of the network
        elif node_degree == 1:
            role = "Foot Worker / Peripheral"
            color = "#4CAF50"  # Green
            size = 15
        else:
            role = "Mid-level Associate"
            color = "#FFA500"  # Orange
            size = 25
            
        # Update PyVis attributes
        G.nodes[node]['title'] = f"Entity: {node}\nRole: {role}\nInfluence Score: {node_influence:.2f}\nDirect Connections: {node_degree}"
        G.nodes[node]['color'] = color
        G.nodes[node]['size'] = size
        G.nodes[node]['group'] = role
        
    return G