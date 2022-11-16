from config import LABELS_DIR

import json
import os

def main():
    with open(os.path.join(LABELS_DIR, "labels_2.json"), "r") as file:
        labels = json.loads(file.read())
    
    new_labels = {
        "2_0": dict(),
        "1_1": dict(),
        "0_2": dict()
    }

    for key in labels:
        outward = key.count(" --> ")
        inward = key.count(" <-- ")
        group_key = f"{outward // 2}_{inward // 2}"

        new_labels[group_key][key] = labels[key]
    
    for group_key in new_labels:
        with open(os.path.join(LABELS_DIR, f"labels_{group_key}.json"), "w+") as file:
            file.write(json.dumps(new_labels[group_key], sort_keys=True, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()