from .node_utils import parse_node

def item_key_to_string(item_key, dictionary, text_senses):
    item_type, item_data = parse_node(item_key)

    if item_type == "LEMMA":
        return item_data
    elif item_type == "SENSE":
        entry = dictionary[item_data]
        return f"{entry['lemma']}.{entry['pos']}"
    elif item_type == "COMPOUND":
        return "In Compound"
    elif item_type == "HAS_SENSE":
        return "Has Sense"
    elif item_type == "TEXT":
        (text_id, _, _) = item_data.split(":")
        return text_senses[text_id]["text"]
    elif item_type == "SYNONYM":
        return "Synonym"
    elif item_type == "CLASS":
        return "Class"
    elif item_type == "DOMAIN":
        return "Domain"


def get_path_str(path, graph, dictionary, text_senses):
    path_str = ""
    for i, node in enumerate(path):
        path_str += item_key_to_string(node, dictionary, text_senses)

        if i < len(path) - 1:
            next_node = path[i + 1]
            out_nodes = [ out_node for _, out_node in graph.out_edges(node)]
            if next_node in out_nodes:
                path_str += " --> "
            else:
                path_str += " <-- "
    return path_str