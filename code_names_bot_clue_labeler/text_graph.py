import networkx as nx

from config import SENSE_EDGES, LEMMA_SENSE_EDGES

def get_key(item_type, data):
    return f"{item_type}|{data}"


def create_text_digraph():
    graph = nx.DiGraph()

    with open(LEMMA_SENSE_EDGES, "r") as file:
        lines = file.read().splitlines()
        for line in lines:
            (lemma, sense, relation_type, data) = line.split("\t")
            data = f"{data}:{lemma}:{sense}"

            edge_key = get_key(relation_type, data)
            graph.add_edge(get_key("LEMMA", lemma), edge_key)
            graph.add_edge(edge_key, get_key("SENSE", sense))
    
    with open(SENSE_EDGES) as file:
        lines = file.read().splitlines()
        for line in lines:
            (from_sense, to_sense, relation_type, relation_data) = line.split("\t")

            # Create an intermediate node representing the edge, so that parallel edges can have separate paths computed.
            # If a sense is linked to another sense in multiple ways (ex. synonym and definition), then they should be listed as separate paths.
            
            if len(relation_data) == 0:
                # If edge has no data (synonym, class, domain edges), then create some data that will make the key unique
                relation_data = f"{from_sense}:{to_sense}"
            relation_key = get_key(relation_type, relation_data)

            from_sense_key = get_key("SENSE", from_sense)
            to_sense_key = get_key("SENSE", to_sense)

            graph.add_edge(from_sense_key, relation_key)
            graph.add_edge(relation_key, to_sense_key)
    
    return graph