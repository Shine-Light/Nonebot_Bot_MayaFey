import re
file = open("in.txt", "w+", encoding="utf-8")
for r in re.findall(r'<div class="collection-avatar__title" data-v-51c84696="">.*?</div>', open("index.txt", "r", encoding="utf-8").read()):
    file.write(r + "\n")
     
