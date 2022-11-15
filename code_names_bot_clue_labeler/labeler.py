from .path_utils import path_to_key
from .text_graph import create_text_digraph
from .path_to_text import print_path_text, path_to_text
from config import TEXT_SENSES, CARDWORDS, LABELS_DIR, DICTIONARY
from .random_path_selector import get_random_path
from .node_utils import parse_node

from argparse import ArgumentParser
import random
import json
import os

def get_expansions():
    parser = ArgumentParser()
    parser.add_argument("n", type=int, default=1)
    args = parser.parse_args()
    return args.n


def valid_clue(cardword, clue):
    return not clue in cardword and not cardword in clue and not " " in clue and not "-" in clue


def select_random_path(cardwords, graph, labeled_paths, expansions):
    cardword = random.choice(cardwords)
    while True:
        path = get_random_path(graph, cardword, expansions)
        
        if path is None:
            continue

        _, clue = parse_node(path[-1])
        sense_path = path[1:-1]

        if not valid_clue(cardword, clue):
            continue
        if path_to_key(graph, sense_path) in labeled_paths:
            continue
        
        return cardword, clue, sense_path


def main():
    with open(CARDWORDS, "r") as file:
        cardwords = file.read().splitlines()

    with open(TEXT_SENSES, "r") as file:
        text_senses = json.loads(file.read())

    expansions = get_expansions()
    labels_path = os.path.join(LABELS_DIR, f"labels_{expansions}.json")
    with open(labels_path, "r") as file:
        labels = json.loads(file.read())

    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())

    text_graph = create_text_digraph()
    labeled_paths = set(labels.keys())

    while(True):
        cardword, clue, path = select_random_path(cardwords, text_graph, labeled_paths, expansions)
        path_key = path_to_key(text_graph, path)
        print_path_text(path_to_text(path, text_graph, dictionary, text_senses))

        input_num = input("Relation [3=WRONG DISAMBIGUATION, 0=UNRELATED, 1=WEAK, 2=STRONG]:")
        
        if not input_num.isdigit():
            break

        labels[path_key] = {
            "cardword": cardword,
            "clue": clue,
            "label": int(input_num)
        }

        with open(labels_path, "w+") as file:
            file.write(json.dumps(labels, sort_keys=True, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()