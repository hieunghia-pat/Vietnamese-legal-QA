import docx
import json
import requests

docx_stream = requests.get("https://ba.hethongphapluat.com/140000/143144/894b93d2201ba2bc59a8643efc5f2d8f.docx", stream=True)
with open("file.docx", "wb") as docx_file:
    docx_file.write(docx_stream.content)

doc = docx.Document("file.docx")
paragraphs = []
for paragraph in doc.paragraphs:
    paragraphs.append(paragraph.text)

json.dump(paragraphs, open("example.json", "w+"), ensure_ascii=False, indent=4)