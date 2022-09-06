import re
file = open("in_name.txt", "w+", encoding="utf-8")
for r in re.findall(r'<div data-v-51c84696="" class="collection-avatar__title">.*?</div>', open("index.txt", "r", encoding="utf-8").read()):
    r = r.replace('<div data-v-51c84696="" class="collection-avatar__title">', "")
    r = r.replace('</div>', "")
    file.write(r + "\n")
     
