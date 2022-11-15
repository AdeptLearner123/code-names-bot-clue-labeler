import random

from .node_utils import get_key, parse_node

def random_select_next_node(graph, path, curr_node, outward, node_types):
    next_nodes = graph.successors(curr_node) if outward else graph.predecessors(curr_node)
    next_nodes = [ node for node in next_nodes if node not in path and parse_node(node)[0] in node_types ]
    if len(next_nodes) == 0:
        return None
    return random.choice(next_nodes)


def get_random_path(graph, lemma, expansions):
    source = get_key("LEMMA", lemma)

    path = [source]
    curr_sense = random_select_next_node(graph, path, source, True, ["SENSE"])
    path.append(curr_sense)
    
    outward = random.random() > 0.5
    for i in range(expansions):
        relation_node = random_select_next_node(graph, path, curr_sense, outward, ["TEXT", "CLASS", "DOMAIN", "SYNONYM"])
        
        if relation_node is None:
            return None

        path.append(relation_node)
        curr_sense = random_select_next_node(graph, path, relation_node, outward, ["SENSE"])
        
        if curr_sense is None:
            return None

        path.append(curr_sense)
        outward = outward and random.random() > 0.5

    target_lemma = random_select_next_node(graph, path, curr_sense, False, ["LEMMA"])
    path.append(target_lemma)
    return path
