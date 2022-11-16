from .path_utils import path_to_key
from .text_graph import create_text_digraph
from .path_to_text import print_path_text, path_to_text
from config import TEXT_SENSES, CARDWORDS, TEXT_LABELS_DIR, DICTIONARY
from .random_path_selector import random_select_next_node
from .node_utils import parse_node, get_key

from argparse import ArgumentParser
import random
import json
import os


def valid_clue(cardword, clue):
    return not clue in cardword and not cardword in clue and not " " in clue and not "-" in clue


def select_random_path(cardwords, graph, labeled_paths):
    while True:
        cardword = random.choice(cardwords)
        source = get_key("LEMMA", cardword)
        path = [source]

        sense = random_select_next_node(graph, path, source, True, ["SENSE"])
        _, sense_id = parse_node(sense)
        path.append(sense)

        text = random_select_next_node(graph, path, sense, True, ["TEXT"])
        _, text_id = parse_node(text)
        text_id, _, _ = text_id.split(":")

        if path_to_key(graph, path) in labeled_paths:
            continue

        return cardword, sense_id, text_id, path[1:]


def get_text_labels(source_sense_id, text_id, text_graph, dictionary, text_senses, path):
    sense_labels = dict()

    for sense in text_senses[text_id]["senses"]:
        sense_id = sense["sense"]
        if sense_id == source_sense_id:
            continue
        sense_node = get_key("SENSE", sense_id)
        text_node = get_key("TEXT", ":".join([text_id, str(sense["start"]), str(sense["len"])]))
        print_path_text(path_to_text(path + [text_node] + [sense_node], text_graph, dictionary, text_senses))
        
        input_num = get_input_num()
        sense_labels[sense_id] = input_num
    
    return sense_labels


def get_input_num():
    while True:
        input_num = input("Relation [3=WRONG DISAMBIGUATION, 0=UNRELATED, 1=WEAK, 2=STRONG]:")
        if input_num.isdigit():
            return int(input_num)


def count_total(labels):
    total = 0
    for key in labels:
        total += len(labels[key]["labels"])
    return total


def main():
    with open(CARDWORDS, "r") as file:
        cardwords = file.read().splitlines()

    with open(TEXT_SENSES, "r") as file:
        text_senses = json.loads(file.read())

    labels_path = os.path.join(TEXT_LABELS_DIR, f"labels_1.json")
    with open(labels_path, "r") as file:
        labels = json.loads(file.read())

    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())

    print("Total labels", count_total(labels))
    
    text_graph = create_text_digraph()
    labeled_paths = set(labels.keys())

    while(True):
        cardword, sense_id, text_id, path = select_random_path(cardwords, text_graph, labeled_paths)
        path_key = path_to_key(text_graph, path)

        text_labels = get_text_labels(sense_id, text_id, text_graph, dictionary, text_senses, path)
        
        labels[path_key] = {
            "cardword": cardword,
            "labels": text_labels
        }

        with open(labels_path, "w+") as file:
            file.write(json.dumps(labels, sort_keys=True, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()