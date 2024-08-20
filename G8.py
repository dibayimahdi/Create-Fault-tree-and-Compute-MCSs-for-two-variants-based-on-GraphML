import cutsets 
import networkx as nx
import matplotlib.pyplot as plt
import pygraphviz as pgv
from itertools import combinations
#########################################################################################
# Step 1: Read the GraphML file
#file_path = "/home/m/Desktop/Graphml/graph.xml"
G = nx.read_graphml('graph3.xml')
# Step 2: Get the labels from the 'label' attribute
labels = nx.get_node_attributes(G, 'label')
info_attributes = nx.get_node_attributes(G, 'info')
variants_attributes = nx.get_node_attributes(G, 'variants')
label_attributes = nx.get_node_attributes(G, 'label')
# Step 3: Filter nodes based on criteria
brakes_v1 = [label_attributes[node] for node, info in info_attributes.items() if info == 'brakes' and 'V1' in variants_attributes[node].split()]
brakes_v2 = [label_attributes[node] for node, info in info_attributes.items() if info == 'brakes' and 'V2' in variants_attributes[node].split()]
# Step 4: Print the results
print("Brakes in Variant1:", brakes_v1)
print("Brakes in Variant2:", brakes_v2)
# Step 2: Get the labels from the 'label' attribute
#variants = nx.get_node_attributes(G, 'variants')
filtered_edges = []
# Iterate over all edges in the graph along with their data and keys
for source, target, data in G.edges(data=True):
    # Check if the 'info' attribute of the source node or target node is 'decentral periphery' or 'switch'
    if (
        (info_attributes[source] == 'decentral periphery' and  info_attributes[target] == 'decentral periphery' ) or  
        (info_attributes[source] == 'switch' and  info_attributes[target] == 'decentral periphery') or
        (info_attributes[source] == 'decentral periphery' and  info_attributes[target] == 'switch')
    ):
        # If the condition is true, add the edge to the filtered_edges list
        filtered_edges.append((source, target, data))
variants_attributes_edges = nx.get_edge_attributes(G, 'variants')
filtered_edges_v1 = [edge for edge in filtered_edges if 'V1' in variants_attributes_edges[(edge[0], edge[1])].split()]
filtered_edges_v2 = [edge for edge in filtered_edges if 'V2' in variants_attributes_edges[(edge[0], edge[1])].split()]
G = nx.DiGraph()
###############################################################FAULT TREE FOR V1
# Add nodes and edges manually to the fault tree of variant 1 (FIRST OR GATE)
G.add_edge("Top event (variant 1)", "OR_Gate_1 (v1)")
G.add_edge("OR_Gate_1 (v1)", "Brake failure (v1)")
#G.add_edge("OR_Gate_1 (v1)", "a failure in the links between the brakes and the ring (v1)")
G.add_edge("OR_Gate_1 (v1)", "At least two link disconnection inside the ring (v1)")
G.add_edge("Brake failure (v1)", "OR_Gate_2 (v1)")
#G.add_edge( "a failure in the links between the brakes and the ring (v1)", "OR_Gate_3 (v1)")
G.add_edge( "At least two link disconnection inside the ring (v1)","VOTING_Gate (2/21) (v1)")
#FIRST OR GATE BRAKES 
for i, brake in enumerate(brakes_v1, start=1):
    G.add_edge("OR_Gate_2 (v1)", f"{brake} (v1)")
    G.add_edge(f"{brake} (v1)", f"Basic Event {i} (v1)")
#SECOND OR GATE INSIDE RINGS
edge_pairs_1 = []  # List to store pairs of reverse edges
for edge1 in filtered_edges_v1:
    source_id_1, target_id_1, attributes_1 = edge1
    edge_id_1 = attributes_1['id']
    
    for edge2 in filtered_edges_v1:
        source_id_2, target_id_2, attributes_2 = edge2
        edge_id_2 = attributes_2['id']
        
        # Check if the source and target of edge1 are reversed in edge2
        if source_id_1 == target_id_2 and target_id_1 == source_id_2:
            # Append the pair of edge IDs to the list
            edge_pairs_1.append((edge_id_1, edge_id_2))
            # Remove the pair from the filtered_edges_v1 to avoid duplicates
            filtered_edges_v1.remove(edge2)
            break  # Move to the next edge1 to avoid duplicates
# Print the edge pairs
print("Possible failures in the ring in Variant 1:",edge_pairs_1)
# Iterate over each pair of edges in edge_pairs
for pair in edge_pairs_1:
    # Add the pair of edges to the graph
    i=i+1
    G.add_edge("VOTING_Gate (2/21) (v1)", f"{pair} (v1)")
    G.add_edge(f"{pair} (v1)", f"Basic Event {i} (v1)")

###############################################################Compute Minimal Cut Sets for Variant 1
# Create the Boolean formula for the voting gate accroding to the contents of edge_pairs_1
# edge_pairs_1 = ["a", "b", "c"]
starting_gate_number = 3

# Generate all pairs (2-combinations) from the list
pairs = list(combinations(edge_pairs_1, 2))

# Each pair will become an AND gate with a label like "G3", "G4", etc.
and_gates = [("G" + str(i + starting_gate_number), "And", list(pair)) for i, pair in enumerate(pairs)]

# The top-level OR gate that combines the names of all AND gates
or_gate = ("G" + str(len(and_gates) + starting_gate_number), "Or", [gate[0] for gate in and_gates])

# Create the final structure for Variant_1
Variant_1 = [
    ("TOP", "Or", [or_gate[0]] + brakes_v1),  # Correct the structure here
    or_gate,  # Define G6 as OR of G3, G4, G5
] + and_gates  # Append the AND gates (G3, G4, G5)

# Print the result
#print("The Boolean function for Variant 1 is:")
#print(Variant_1)
print("Minimal Cut Sets for Variant 1 is:")
cs = cutsets.mocus (Variant_1)
print (cs)
###############################################################FAULT TREE FOR V2
# Add nodes and edges manually to the fault tree of variant 2 
G.add_edge("Top event (variant 2)", "OR_Gate_1 (v2)")
G.add_edge("OR_Gate_1 (v2)", "Brake failure (v2)")
#G.add_edge("OR_Gate_1 (v2)", "a failure in the links between the brakes and the ring (v2)")
G.add_edge("OR_Gate_1 (v2)", "At least two link disconnection inside the ring (v2)")
G.add_edge("Brake failure (v2)", "OR_Gate_2 (v2)")
#G.add_edge( "a failure in the links between tvoraussichtlich he brakes and the ring (v2)", "OR_Gate_3 (v2)")
G.add_edge( "At least two link disconnection inside the ring (v2)","VOTING_Gate (2/25) (v2)")
#FIRST OR GATE BRAKES 
for i, brake in enumerate(brakes_v2, start=1):
    G.add_edge("OR_Gate_2 (v2)", f"{brake} (v2)")
    G.add_edge(f"{brake} (v2)", f"Basic Event {i} (v2)")
#SECOND OR GATE INSIDE RINGS
edge_pairs_2 = []  # List to store pairs of reverse edges
for edge1 in filtered_edges_v2:
    source_id_1, target_id_1, attributes_1 = edge1
    edge_id_1 = attributes_1['id']
    
    for edge2 in filtered_edges_v2:
        source_id_2, target_id_2, attributes_2 = edge2
        edge_id_2 = attributes_2['id']
        
        # Check if the source and target of edge1 are reversed in edge2
        if source_id_1 == target_id_2 and target_id_1 == source_id_2:
            # Append the pair of edge IDs to the list
            edge_pairs_2.append((edge_id_1, edge_id_2))
            # Remove the pair from the filtered_edges_v1 to avoid duplicates
            filtered_edges_v2.remove(edge2)
            break  # Move to the next edge1 to avoid duplicates

# Print the edge pairs

print("Possible failures in the ring in Variant 2:",edge_pairs_2)
# Iterate over each pair of edges in edge_pairs
for pair in edge_pairs_2:
    # Add the pair of edges to the graph
    i=i+1
    G.add_edge("VOTING_Gate (2/25) (v2)", f"{pair} (v2)")
    G.add_edge(f"{pair} (v2)", f"Basic Event {i} (v2)")
###############################################################Compute Minimal Cut Sets for Variant 2
# Create the Boolean formula for the voting gate accroding to the contents of edge_pairs_2
starting_gate_number = 3

# Generate all pairs (2-combinations) from the list
pairs = list(combinations(edge_pairs_2, 2))

# Each pair will become an AND gate with a label like "G3", "G4", etc.
and_gates = [("G" + str(i + starting_gate_number), "And", list(pair)) for i, pair in enumerate(pairs)]

# The top-level OR gate that combines the names of all AND gates
or_gate = ("G" + str(len(and_gates) + starting_gate_number), "Or", [gate[0] for gate in and_gates])

# Create the final structure for Variant_1
Variant_2 = [
    ("TOP", "Or", [or_gate[0]] + brakes_v2),  # Correct the structure here
    or_gate,  # Define G6 as OR of G3, G4, G5
] + and_gates  # Append the AND gates (G3, G4, G5)

# Print the result
#print("The Boolean function for Variant 2 is:")
#print(Variant_2)
print("Minimal Cut Sets for Variant 2 is:")
cs = cutsets.mocus (Variant_2)
print (cs)


################################################################ Create a PyGraphviz graph from the NetworkX graph
A = nx.nx_agraph.to_agraph(G)
# Customize node and edge attributes if needed
A.node_attr.update(shape="box")  # Represent components and gates as boxes
A.node_attr.update(color="lightblue")  # Set color for components
A.node_attr.update(style="filled")
# Draw the graph
A.layout(prog="dot")
A.draw("fault_tree.png")
# Show the plot
plt.imshow(plt.imread("fault_tree.png"))
plt.axis("off")
plt.show()
