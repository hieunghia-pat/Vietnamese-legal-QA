from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import json
import os
import re

def parsing_information(div):
    assert div.h2.text.lower() == "thông tin"
    
    table_data = {}
    rows = div.table.tbody.find_all("tr")
    for row in rows:
        data = row.find_all("td")
        key = re.sub("\n", "", data[0].text)
        value = re.sub("\n", "", data[1].text)
        table_data[key] = value

    return table_data

def parsing_methodology(div):
    assert div.h2.text.lower() == "cách thực hiện"

    table_data = {
        "trình tự thực hiện": None,
        "điều kiện thực hiện": None
    }
    table_1, table_2 = div.find_all("table")
    
    ths = table_1.find_all("th")
    trs = table_1.find_all("tr")
    item = {
        ths[0].text.strip(): [],
        ths[1].text.strip(): []
    }
    for tr in trs:
        td_1, td_2 = tr.find_all("td")
        item[ths[0].text.strip()].append(td_1.text.strip())
        item[ths[1].text.strip()].append(td_2.text.strip())
    table_data["trình tự thực hiện"] = item

    ths = table_2.find_all("th")
    td_1, td_2 = table_2.find_all("td")
    item = {
        ths[0].text.strip(): [],
        ths[1].text.strip(): []
    }
    item[ths[0].text.strip()].append(td_1.text.strip())
    item[ths[1].text.strip()].append(td_2.text.strip())
    table_data["điều kiện thực hiện"] = item

    return table_data

def parsing_file(div):
    pass

def parsing_form(div):
    pass

def parsing_expense(div):
    pass

def parsing_legal_basis(div):
    pass

def parsing_relevant_legal_methodology(div):
    pass

MAX_PAGE = 40
THONG_TIN = "thông tin"
CACH_THUC_HIEN = "cách thực hiện"
THANH_PHAN_HO_SO = "thành phần hồ sơ"
BIEU_MAU = "biểu mẫu"
PHI_LE_PHI = "phí, lệ phí"
CO_SO_PHAP_LY = "cơ sở pháp lý"
TTHC_LIEN_QUAN = "TTHC liên quan"

parsed_link = set()
data = []
domain = "https://hethongphapluat.com"
topic = "thu-tuc-hanh-chinh"
for page in range(MAX_PAGE):
    url = f"{os.path.join(domain, topic)}_page-{page}.html"
    
    main_soup = BeautifulSoup(requests.get(url).content, features="lxml")
    session = requests.Session()

    print(url)
    
    with tqdm(main_soup.find_all("div", class_="list-body")) as pb:
        for div in pb:
            link = div.find("a")["href"]
            title = div.find("a")["title"]
            
            pb.set_postfix_str(f"Parsing \"{title}\"")

            if link in parsed_link:
                continue
            
            parsed_link.add(link)

            content = session.get(os.path.join(domain, link)).content
            soup = BeautifulSoup(content, features="lxml")
            item = {
                THONG_TIN: [],
                CACH_THUC_HIEN: [],
                THANH_PHAN_HO_SO: [],
                BIEU_MAU: [],
                PHI_LE_PHI: [],
                CO_SO_PHAP_LY: [],
                TTHC_LIEN_QUAN: []
            }

            divs = soup.find_all("div", class_="tab-pane")

            item[THONG_TIN].append(parsing_information(divs[0]))
            item[CACH_THUC_HIEN].append(parsing_methodology(divs[1]))
            item[THANH_PHAN_HO_SO].append(parsing_file(divs[2]))
            item[BIEU_MAU].append(parsing_form(divs[3]))
            item[PHI_LE_PHI].append(parsing_expense(divs[4]))
            item[CO_SO_PHAP_LY].append(parsing_legal_basis(divs[5]))
            item[TTHC_LIEN_QUAN].append(parsing_relevant_legal_methodology(divs[6]))

            data.append(item)

json.dump(data, open("hethongphapluat-thutuchanhchinh.json", "w+"), ensure_ascii=False, indent=4)
