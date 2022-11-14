from .node_utils import parse_node
from colorama import Fore, Style

OPEN_MARKER = "<src>"
CLOSE_MARKER = "</src>"
LINK_OPEN_MARKER = "<link>"
LINK_CLOSE_MARKER = "</link>"

def annotate_compound(compound, token):
    if token.lower() not in compound.lower():
        return None
    
    sep_tokens = ["-", " "]
    start = compound.lower().index(token.lower())
    end = start + len(token)

    if (start == 0 or compound[start - 1] in sep_tokens) and (end == len(compound) or compound[end] in sep_tokens):
        return compound[:start] + OPEN_MARKER + compound[start:end] + CLOSE_MARKER + compound[end:]
    
    return None


def annotate_text(text, source_lemma, source_relation):
    if source_relation == "COMPOUND":
        return annotate_compound(text, source_lemma)
    else:
        return OPEN_MARKER + text + CLOSE_MARKER


def compound_path_to_text(source_lemma, target_lemma, middle_nodes, dictionary):
    sense = parse_node(middle_nodes[0])[1]
    sense_text = dictionary[sense]["lemma"]
    sense_text = annotate_compound(sense_text, source_lemma)

    if sense_text is None:
        return None
    
    sense_text = annotate_compound(sense_text, target_lemma)
    return sense_text


def split_path(graph, middle_nodes):
    for i in range(len(middle_nodes) - 1):
        from_node = middle_nodes[i]
        to_node = middle_nodes[i + 1]
        out_nodes = [ node for _, node in graph.out_edges(from_node) ]
        if to_node not in out_nodes:
            return middle_nodes[:i + 1], middle_nodes[i:]
    
    return middle_nodes, []


def sem_link_to_text(from_sense, to_sense, dictionary, relation_text, source_lemma, source_relation, target_lemma, target_relation):
    source_text = dictionary[from_sense]["lemma"]
    if source_lemma is not None:
        source_text = annotate_text(source_text, source_lemma, source_relation)
    else:
        source_text = LINK_OPEN_MARKER + source_text + LINK_CLOSE_MARKER
    
    target_text = dictionary[to_sense]["lemma"]
    if target_lemma is not None:
        target_text = annotate_text(target_text, target_lemma, target_relation)
    else:
        target_text = LINK_OPEN_MARKER + target_text + LINK_CLOSE_MARKER

    return f"{source_text} <{relation_text}> {target_text}"


def text_link_to_text(from_sense, relation_data, dictionary, text_senses, source_lemma, source_relation, target_lemma, target_relation):
    source_text = dictionary[from_sense]["lemma"]
    if source_lemma is not None:
        source_text = annotate_text(source_text, source_lemma, source_relation)
    else:
        source_text = LINK_OPEN_MARKER + source_text + LINK_CLOSE_MARKER

    text_id, start, length = relation_data.split(":")
    start = int(start)
    length = int(length)
    text = text_senses[text_id]["text"]

    target_text = text[start:start + length]
    if target_lemma is not None:
        target_text = annotate_text(target_text, target_lemma, target_relation)
    else:
        target_text = LINK_OPEN_MARKER + target_text + LINK_CLOSE_MARKER
    text = text[:start] + target_text + text[start + length:]
    return f"{source_text} <TEXT> {text}"


def path_link_to_text(from_node, to_node, relation, dictionary, text_senses, source_lemma = None, source_relation = None, target_lemma = None, target_relation = None):
    _, from_sense = parse_node(from_node)
    _, to_sense = parse_node(to_node)
    relation_type, relation_data = parse_node(relation)
    if relation_type == "TEXT":
        return text_link_to_text(from_sense, relation_data, dictionary, text_senses, source_lemma, source_relation, target_lemma, target_relation)
    return sem_link_to_text(from_sense, to_sense, dictionary, relation_type, source_lemma, source_relation, target_lemma, target_relation)


def half_path_to_text(path_nodes, source_lemma, source_relation, dictionary, text_senses, target_lemma = None, target_relation = None):
    link_texts = []
    for i in range(0, len(path_nodes) - 1, 2):
        from_node = path_nodes[i]
        relation = path_nodes[i + 1]
        to_node = path_nodes[i + 2]

        link_source_lemma, link_source_relation, link_target_lemma, link_target_relation = None, None, None, None
        if i == 0:
            link_source_lemma = source_lemma
            link_source_relation = source_relation
        if i + 3 >= len(path_nodes):
            link_target_lemma = target_lemma
            link_target_relation = target_relation
        link_texts.append(path_link_to_text(from_node, to_node, relation, dictionary, text_senses, link_source_lemma, link_source_relation, link_target_lemma, link_target_relation))
    return link_texts


def path_to_text(path, graph, dictionary, text_senses):
    source_lemma = parse_node(path[0])[1]
    source_relation = parse_node(path[1])[0]

    target_lemma = parse_node(path[-1])[1]
    target_relation = parse_node(path[-2])[0]

    middle_nodes = path[2:-2]

    if len(middle_nodes) == 1:
        # Path is a single compound word
        return compound_path_to_text(source_lemma, target_lemma, middle_nodes, dictionary)
    
    forward_path, backward_path = split_path(graph, middle_nodes)
    backward_path = list(reversed(backward_path))

    if len(forward_path) == 0:
        # Entire path is backwards, so attach source lemma to backwards path
        link_texts = list(reversed(half_path_to_text(backward_path, target_lemma, target_relation, dictionary, text_senses, source_lemma, source_relation)))
    elif len(backward_path) == 0:
        # Entire path is forwards, so attach target lemma to forwards path
        link_texts = half_path_to_text(forward_path, source_lemma, source_relation, dictionary, text_senses, target_lemma, target_relation)
    else:
        # Generate forward and backward paths separately
        link_texts = half_path_to_text(forward_path, source_lemma, source_relation, dictionary, text_senses) + list(reversed(half_path_to_text(backward_path, target_lemma, target_relation, dictionary, text_senses)))
    
    return ". ".join(link_texts)


def print_path_text(path_text):
    path_text = path_text.replace(OPEN_MARKER, Fore.RED, 1)
    path_text = path_text.replace(OPEN_MARKER, Fore.GREEN, 1)
    path_text = path_text.replace(CLOSE_MARKER, Style.RESET_ALL)
    path_text = path_text.replace(LINK_OPEN_MARKER, Fore.YELLOW)
    path_text = path_text.replace(LINK_CLOSE_MARKER, Style.RESET_ALL)
    print(path_text)