from .text_graph import create_text_digraph
from .path_to_text import print_path_text, path_to_text
from config import TEXT_SENSES, CARDWORDS, LABELS, DICTIONARY
import random
from .paths_matcher import match_paths
from .node_utils import parse_node
from tqdm import tqdm
import json

def select_random_text(cardwords, text_graph, outward):
    cardword = random.choice(cardwords)
    key = f"LEMMA|{cardword}"
    senses = []
    for _, node in text_graph.out_edges(key):
        node_type = node.split("|")[0]
        if node_type == "HAS_SENSE":
            senses.append()


def get_possible_paths(graph, cardwords):
    possible_paths = []
    for cardword in tqdm(cardwords):
        cardword_possible_paths = match_paths(graph, f"LEMMA|{cardword}", [
            {
                "node_types": ["HAS_SENSE"],
                "times": 1,
                "out_only": True
            },
            {
                "node_types": ["SENSE"],
                "times": 1,
                "out_only": True
            },
            {
                "node_types": ["TEXT"],
                "times": 1
            },
            {
                "node_types": ["SENSE"],
                "times": 1,
                "in_only": True
            },
            {
                "node_types": ["HAS_SENSE"],
                "times": 1,
                "in_only": True
            },
            {
                "node_type": "LEMMA",
                "times": 1,
                "in_only": True
            }
        ])
        
        filtered_paths = []
        for path in cardword_possible_paths:
            target_lemma = parse_node(path[-1])[1]
            if cardword not in target_lemma:
                filtered_paths.append(path)

        possible_paths += filtered_paths
    return possible_paths


def path_to_key(path):
    return "---".join(path)


def key_to_path(path_key):
    return path_key.split("---")


def main():
    with open(CARDWORDS, "r") as file:
        cardwords = file.read().splitlines()

    with open(TEXT_SENSES, "r") as file:
        text_senses = json.loads(file.read())

    with open(LABELS, "r") as file:
        labels = json.loads(file.read())

    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())

    text_graph = create_text_digraph()
    possible_paths = get_possible_paths(text_graph, cardwords)
    print("Possible paths:", len(possible_paths))    
    path_keys = [ path_to_key(path) for path in possible_paths ]

    path_keys = list(set(path_keys).difference(set(labels.keys())))

    while(True):
        path_key = path_keys.pop(random.randrange(len(path_keys)))
        path = key_to_path(path_key)
        print_path_text(path_to_text(path, text_graph, dictionary, text_senses))

        input_num = input("Relation [0=UNRELATED, 1=WEAK, 2=STRONG]:")
        
        if not input_num.isdigit():
            break

        labels[path_key] = int(input_num)

        with open(LABELS, "w+") as file:
            file.write(json.dumps(labels, sort_keys=True, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()