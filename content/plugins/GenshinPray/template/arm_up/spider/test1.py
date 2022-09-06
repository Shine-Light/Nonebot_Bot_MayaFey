import re
file = open("in_img.txt", "w+", encoding="utf-8")
for r in re.findall(r'<div data-v-51c84696="" class="collection-avatar__icon" data-src=".*?\.png\?x-oss-process=image/quality,q_75/resize,s_120', open("index.txt", "r", encoding="utf-8").read()):
    r = r.replace('<div data-v-51c84696="" class="collection-avatar__icon" data-src="', "")
    file.write(r + "\n")
     
