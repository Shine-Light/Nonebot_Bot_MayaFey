import re
file = open("in.txt", "w+", encoding="utf-8")
for r in re.findall(r'url\(.*?\)', open("index.txt", "r", encoding="utf-8").read()):
    file.write(r + "\n")
     
