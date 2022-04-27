from os.path import dirname
from collections import  defaultdict
import json

class DataLoader:
    def __init__(self, path_name: str):

        self.path = dirname(__file__)+ '/' + path_name        
        try:
            with open(self.path, encoding="UTF-8") as f:
                data = json.load(f)
            self.data = defaultdict(list, data)
        except:
            with open(self.path, 'w+', encoding="UTF-8") as f:
                f.write('{}')
            self.data = defaultdict(list)
        
    

    def save(self):
        with open(self.path, 'w+', encoding="UTF-8") as f :
                tojson = json.dumps(self.data,sort_keys=True, ensure_ascii=False, indent=4,separators=(',',': '))
                f.write(tojson)