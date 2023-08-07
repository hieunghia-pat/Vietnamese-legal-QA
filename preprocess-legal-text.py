import json
import os
import re
from tqdm import tqdm

BASE_DIR = "categorized-vanban"
DEST_DIR = "preprocessed-legal-texts"

for SUB_DIR in tqdm(os.listdir(BASE_DIR)):
    for ith, json_file in enumerate(os.listdir(os.path.join(BASE_DIR, SUB_DIR))[5:], 1):
        try:
            data = json.load(open(os.path.join(BASE_DIR, SUB_DIR, json_file)))
        except:
            print(json_file)
        passage: str = data["passage"]

        passages = passage.split("\n\n")
        passages = [re.sub("[\n\r\t]", " ", passage) for passage in passages]
        passages = [re.sub("\s+", r" ", passage) for passage in passages]
        passage = "\n".join(passages)

        with open(os.path.join(DEST_DIR, json_file), "w+") as file:
            json.dump({
                **data,
                "passage": passage
            }, file, ensure_ascii=False, indent=4)