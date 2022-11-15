from .node_utils import parse_node
from colorama import Fore, Style

OPEN_MARKER = "<src>"
CLOSE_MARKER = "</src>"
LINK_OPEN_MARKER = "<link>"
LINK_CLOSE_MARKER = "</link>"


def split_path(graph, middle_nodes):
    for i in range(len(middle_nodes) - 1):
        from_node = middle_nodes[i]
        to_node = middle_nodes[i + 1]
        if to_node not in graph.successors(from_node):
            return middle_nodes[:i + 1], middle_nodes[i:]
    
    return middle_nodes, middle_nodes[-1:]


def annotate(text, is_source):
    if is_source:
        return f"{OPEN_MARKER}{text}{CLOSE_MARKER}"
    return f"{LINK_OPEN_MARKER}{text}{LINK_CLOSE_MARKER}"


def sem_link_to_text(from_sense, to_sense, dictionary, relation_text, highlight_from, highlight_to):
    source_text = dictionary[from_sense]["lemma"]
    source_text = annotate(source_text, highlight_from)
    
    target_text = dictionary[to_sense]["lemma"]
    target_text = annotate(target_text, highlight_to)

    return f"{source_text} <{relation_text}> {target_text}"


def text_link_to_text(from_sense, relation_data, dictionary, text_senses, highlight_from, highlight_to):
    source_text = dictionary[from_sense]["lemma"]
    source_text = annotate(source_text, highlight_from)

    text_id, start, length = relation_data.split(":")
    start = int(start)
    length = int(length)
    text = text_senses[text_id]["text"]

    target_text = text[start:start + length]
    target_text = annotate(target_text, highlight_to)
    text = text[:start] + target_text + text[start + length:]
    return f"{source_text} <TEXT> {text}"


def path_link_to_text(from_node, to_node, relation, dictionary, text_senses, highlight_from, highlight_to):
    _, from_sense = parse_node(from_node)
    _, to_sense = parse_node(to_node)
    relation_type, relation_data = parse_node(relation)
    if relation_type == "TEXT":
        return text_link_to_text(from_sense, relation_data, dictionary, text_senses, highlight_from, highlight_to)
    return sem_link_to_text(from_sense, to_sense, dictionary, relation_type, highlight_from, highlight_to)


def half_path_to_text(path_nodes, dictionary, text_senses, highlight_tail):
    link_texts = []
    for i in range(0, len(path_nodes) - 1, 2):
        from_node = path_nodes[i]
        relation = path_nodes[i + 1]
        to_node = path_nodes[i + 2]

        highlight_from = i == 0
        highlight_to = i + 3 >= len(path_nodes) and highlight_tail
        link_texts.append(path_link_to_text(from_node, to_node, relation, dictionary, text_senses, highlight_from, highlight_to))
    return link_texts


def path_to_text(path, graph, dictionary, text_senses):
    forward_path, backward_path = split_path(graph, path)
    backward_path = list(reversed(backward_path))

    if len(forward_path) == 1:
        # Entire path is backwards, so attach source lemma to backwards path
        link_texts = list(reversed(half_path_to_text(backward_path, dictionary, text_senses, True)))
    elif len(backward_path) == 1:
        # Entire path is forwards, so attach target lemma to forwards path
        link_texts = half_path_to_text(forward_path, dictionary, text_senses, True)
    else:
        # Generate forward and backward paths separately
        link_texts = half_path_to_text(forward_path, dictionary, text_senses, False) + list(reversed(half_path_to_text(backward_path, dictionary, text_senses, False)))
    
    return ". ".join(link_texts)


def print_path_text(path_text):
    path_text = path_text.replace(OPEN_MARKER, Fore.RED, 1)
    path_text = path_text.replace(OPEN_MARKER, Fore.GREEN, 1)
    path_text = path_text.replace(CLOSE_MARKER, Style.RESET_ALL)
    path_text = path_text.replace(LINK_OPEN_MARKER, Fore.YELLOW)
    path_text = path_text.replace(LINK_CLOSE_MARKER, Style.RESET_ALL)
    print(path_text)