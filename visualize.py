from pyvis.network import Network

def generate_html_graph(nx_graph, output_file="network_graph.html"):
    """
    Takes a NetworkX graph and generates an interactive HTML visualization.
    Leaders are Red, Places are Yellow, and standard entities are White.
    """
    net = Network(height="800px", width="100%", bgcolor="#1a1a1a", font_color="white", directed=True)
    net.from_nx(nx_graph)
    
    # Smart filtering for Places
    targets_of_location = set()
    action_performers = set()
    
    for u, v, data in nx_graph.edges(data=True):
        action_performers.add(u)  # 'u' is the source/suspect performing an action
        if data.get('label') == 'LOCATED_AT':
            targets_of_location.add(v)
            
    # A true place is targeted by LOCATED_AT, but NEVER performs an action itself
    places = targets_of_location - action_performers
            
    # Apply custom coloring rules to nodes
    for node in net.nodes:
        node_id = node['id']
        
        # Base styling for all nodes
        node['borderWidth'] = 2
        node['font'] = {'color': 'white', 'size': 18, 'face': 'arial'}
        
        # Color mapping based on role and location
        if node.get('group') == "Leader / Kingpin":
            node['color'] = "#FF4B4B"  # Red for Leaders
        elif node_id in places:
            node['color'] = "#FFD700"  # Yellow for Places
        else:
            node['color'] = "#ffffff"  # White for standard people
            
    # Keep edges and edge labels clean and visible against the dark background
    for edge in net.edges:
        edge['color'] = "#ffffff"
        edge['font'] = {'color': '#cccccc', 'size': 12, 'align': 'middle', 'background': '#1a1a1a'}
        
    # Configure physics so nodes are properly spaced
    net.repulsion(
        node_distance=300, 
        central_gravity=0.1, 
        spring_length=200, 
        spring_strength=0.05, 
        damping=0.09
    )
    
    net.save_graph(output_file)
    return output_file
