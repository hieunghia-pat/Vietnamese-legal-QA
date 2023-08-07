import json
import os
import re
from typing import Tuple, Union
import pandas as pd
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--van-ban", required=True, type=str)

args = parser.parse_args()

# Phần > Chương > Mục > Tiểu mục > Điều > Khoản > Điểm

LEVEL = {
    "phần": 5,
    "chương": 4,
    "mục": 3,
    "tiểu mục": 2,
    "điều": 1
}

BASE_DIR = "categorized-vanban"
DEST_DIR = "structured-texts"
SUB_DIR = args.van_ban
if not os.path.isdir(os.path.join(DEST_DIR, SUB_DIR)):
    os.makedirs(os.path.join(DEST_DIR, SUB_DIR))

pattern = r"<newline>(Phần|Chương|Mục|Tiểu\s+[Mm]ục|Điều)[\s+]?[0-9IVX]+[:.)a-z]?[\s]?(<newline>)?"
titles = ["Phần", "Chương", "Mục", "Tiểu mục", "Điều"]
def process_part_number(part_number: str) -> Tuple[Union[str, None], str]:
    part_number = re.sub("[.):]", "", part_number)
    tmp = part_number.split()
    if tmp[0] == "Tiểu":
        part = " ".join(tmp[:-1])
        number = tmp[-1]
    else:
        part = tmp[0]
        number = " ".join(tmp[1:])

    return part, number

def process_part_number_within_content(content: str) -> Tuple[Union[str, None], str]:
    # header or footer
    sub_pattern = r"(Phần|Chương|Mục|Tiểu\s+[Mm]ục|Điều)\s+[0-9IVX]+(?:[:.)a-z])?(:?\s+)?(?:cũ)?(?:mới)?"
    if not (content.lower().startswith("phần") or content.lower().startswith("chương") \
            or content.lower().startswith("mục") or content.lower().startswith("tiểu mục") \
            or content.lower().startswith("điều")):
        return content, None
    
    try:
        part_number = re.search(sub_pattern, content).group()
    except:
        print(content)
        raise
    return process_part_number(part_number)

def process_phan(row: pd.Series) -> Union[dict, None]:
    title = row["Phần.title"]
    number = row["Phần.number"]
    if number is None:
        return None
    
    return {
        "number": number,
        "title": title
    }

def process_chuong(row: pd.Series) -> dict:
    title = row["Chương.title"]
    number = row["Chương.number"]
    if number is None:
        return None
    rt = {
        "number": number,
        "title": title
    }
    phan_number = row["Phần.number"]
    if phan_number is not None:
        rt = {
            **rt,
            "Phần": phan_number
        }
    
    return rt

def process_muc(row: pd.Series) -> dict:
    title = row["Mục.title"]
    number = row["Mục.number"]
    if number is None:
        return None
    rt = {
        "number": number,
        "title": title
    }
    phan_number = row["Phần.number"]
    if phan_number is not None:
        rt = {
            **rt,
            "Phần": phan_number
        }
    chuong_number = row["Chương.number"]
    if chuong_number is not None:
        rt = {
            **rt,
            "Chương": chuong_number
        }

    return rt

def process_tieumuc(row: pd.Series) -> dict:
    title = row["Tiểu mục.title"]
    number = row["Tiểu mục.number"]
    if number is None:
        return None
    rt = {
        "number": number,
        "title": title
    }
    phan_number = row["Phần.number"]
    if phan_number is not None:
        rt = {
            **rt,
            "Phần": phan_number
        }
    chuong_number = row["Chương.number"]
    if chuong_number is not None:
        rt = {
            **rt,
            "Chương": chuong_number
        }
    muc_number = row["Mục.number"]
    if muc_number is not None:
        rt = {
            **rt,
            "Mục": muc_number
        }

    return rt

def process_dieu(row: pd.Series) -> dict:
    title = row["Điều.title"]
    number = row["Điều.number"]

    assert (number is not None) and (title is not None)
    rt = {
        "number": number,
        "title": title
    }
    phan_number = row["Phần.number"]
    if phan_number is not None:
        rt = {
            **rt,
            "Phần": phan_number
        }
    chuong_number = row["Chương.number"]
    if chuong_number is not None:
        rt = {
            **rt,
            "Chương": chuong_number
        }
    muc_number = row["Mục.number"]
    if muc_number is not None:
        rt = {
            **rt,
            "Mục": muc_number
        }
    tieumuc_number = row["Tiểu mục.number"]
    if tieumuc_number is not None:
        rt = {
            **rt,
            "Tiểu mục": tieumuc_number
        }

    return rt

for json_file in tqdm(os.listdir(os.path.join(BASE_DIR, SUB_DIR))):
    data = json.load(open(os.path.join(BASE_DIR, SUB_DIR, json_file)))
    passage: str = data["passage"]
    if passage == "":
        print(json_file)
        continue

    passage = re.sub("Điều", "Điều ", passage)
    passage = re.sub("Chương", "Chương ", passage)
    passage = re.sub("Mục", "Mục ", passage)
    passage = re.sub("Phần", "Phần ", passage)
    passage = re.sub("Tiểu mục", "Tiểu mục ", passage)
    filename = re.sub(".json", "", json_file)

    with open(f"debug/{filename}.txt", "w+") as file:
        file.write(passage)

    passages = re.split("\n\n", passage)
    passages = [re.sub("[\n\r\t]+", " ", passage) for passage in passages]
    passages = [re.sub("\s+", r" ", passage).strip() for passage in passages]
    while "" in passages:
        passages.remove("")
    while " " in passages:
        passages.remove(" ")
    passages = [passage for passage in passages]
    passage = "<newline>".join(passages)

    with open(f"debug/after_preprocessed_{filename}.txt", "w+") as file:
        file.write(passage)

    matches = re.finditer(pattern, passage)
    part_numbers = [match.group().strip() for match in matches]
    part_numbers = [re.sub("<newline>", "", part_number) for part_number in part_numbers]
    part_numbers = [re.sub("[:.)]", "", part_number) for part_number in part_numbers]
    for part_number in part_numbers:
        pattern_part_number = part_number.replace(".", "\.")
        pattern_part_number = pattern_part_number.replace(")", "\)")
        passage = re.sub(f"<newline>{pattern_part_number}", f"<split>{part_number}", passage)

    with open(f"debug/after_splitted_{filename}.txt", "w+") as file:
        file.write(passage)

    passage = re.sub("<newline>", "\n", passage)
    passage = re.sub("(<split>)+", "<split>", passage)
    # word_split_matches = re.finditer(r"[A-Za-záÁàÀảẢãÃạẠăĂắẮằĂdẳẲẵẴặẶâÂấẤầẦẩẨẫẪậẬđĐéÉèÈẻẺẽẼẹẸêÊếẾềỀểỂễỄệỆóÓòÒỏỎõÕọỌôÔốỐồỒổỔỗỖộỘơƠớỚờỜởỞỡỠợỢúÚùÙủỦũŨụỤưƯứỨừỪửỬữỮựỰíÍìÌỉỈĩĨịỊýÝỳỲỷỶỹỸỵỴ]+<split>[A-Za-záÁàÀảẢãÃạẠăĂắẮằĂdẳẲẵẴặẶâÂấẤầẦẩẨẫẪậẬđĐéÉèÈẻẺẽẼẹẸêÊếẾềỀểỂễỄệỆóÓòÒỏỎõÕọỌôÔốỐồỒổỔỗỖộỘơƠớỚờỜởỞỡỠợỢúÚùÙủỦũŨụỤưƯứỨừỪửỬữỮựỰíÍìÌỉỈĩĨịỊýÝỳỲỷỶỹỸỵỴ]+", passage)
    # word_split_matches = re.finditer(r"<split>", passage)
    # for matched in word_split_matches:
    #     replaced_split = re.sub("<split>", " ", matched.group())
    #     passage = re.sub(matched.group(), replaced_split, passage)

    phans = []
    phan_contents = []
    phan_number = None
    phan_content = None
    chuongs = []
    chuong_contents = []
    chuong_number = None
    chuong_content = None
    mucs = []
    muc_contents = []
    muc_number = None
    muc_content = None
    tieumucs = []
    tieumuc_contents = []
    tieumuc_number = None
    tieumuc_content = None
    dieus = []
    dieu_contents = []
    dieu_number = None
    dieu_content = None
    contents = passage.split("<split>")

    with open(f"debug/list_{filename}.txt", "w+") as file:
        for content in contents:
            file.write(content + "\n")

    while "" in contents:
        contents.remove("")
    while " " in contents:
        contents.remove(" ")
    for content in contents[1:]:
        try:
            part, number = process_part_number_within_content(content)
        except:
            print(json_file)
            raise
        part_number = f"{part} {number}"
        processed_content = re.sub(f"{part_number}[.:)]?", "", content)
        processed_content = processed_content.strip()
    
        if LEVEL[part.lower()] == 5:
            phan_number = number
            phan_content = processed_content
            chuong_number = None
            chuong_content = None
            muc_number = None
            muc_content = None
            tieumuc_number = None
            tieumuc_content = None
            dieu_number = None
            dieu_content = None
        if LEVEL[part.lower()] == 4:
            chuong_number = number
            chuong_content = processed_content
            muc_number = None
            muc_content = None
            tieumuc_number = None
            tieumuc_content = None
            dieu_number = None
            dieu_content = None
        if LEVEL[part.lower()] == 3:
            muc_number = number
            muc_content = processed_content
            tieumuc_number = None
            tieumuc_content = None
            dieu_number = None
            dieu_content = None
        if LEVEL[part.lower()] == 2:
            tieumuc_number = number
            tieumuc_content = processed_content
            dieu_number = None
            dieu_content = None
        if LEVEL[part.lower()] == 1:
            dieu_number = number
            dieu_content = processed_content
        
        phans.append(phan_number)
        phan_contents.append(phan_content)
        chuongs.append(chuong_number)
        chuong_contents.append(chuong_content)
        mucs.append(muc_number)
        muc_contents.append(muc_content)
        tieumucs.append(tieumuc_number)
        tieumuc_contents.append(tieumuc_content)
        dieus.append(dieu_number)
        dieu_contents.append(dieu_content)

    structure = {
        "Header": contents[0],
        "Phần": [],
        "Chương": [],
        "Mục": [],
        "Tiểu Mục": [],
        "Điều": []
    }
    df = pd.DataFrame({
        "Phần.number": phans,
        "Phần.title": phan_contents,
        "Chương.number": chuongs,
        "Chương.title": chuong_contents,
        "Mục.number": mucs,
        "Mục.title": muc_contents,
        "Tiểu mục.number": tieumucs,
        "Tiểu mục.title": tieumuc_contents,
        "Điều.number": dieus,
        "Điều.title": dieu_contents
    })

    for ith, row in df.iterrows():
        if row["Điều.number"] is None:
            continue
        phan = process_phan(row)
        if phan is not None and phan not in structure["Phần"]:
            structure["Phần"].append(phan)
        chuong = process_chuong(row)
        if chuong is not None and chuong not in structure["Chương"]:
            structure["Chương"].append(chuong)
        muc = process_muc(row)
        if muc is not None and muc not in structure["Mục"]:
            structure["Mục"].append(muc)
        tieumuc = process_tieumuc(row)
        if tieumuc is not None and tieumuc not in structure["Tiểu Mục"]:
            structure["Tiểu Mục"].append(tieumuc)
        dieu = process_dieu(row)
        if dieu is not None and dieu not in structure["Điều"]:
            structure["Điều"].append(dieu)

    json.dump(structure, open(f"structured-texts/{args.van_ban}/{json_file}", "w+"), ensure_ascii=False, indent=4)