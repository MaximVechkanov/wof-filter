#!/bin/python3

import yaml
from pprint import pprint

with open("bites_unsorted.yaml") as bitesFile:
    bites = yaml.safe_load(bitesFile)
    
# print(bites)

bites.sort()

with open("bites.yaml", "w") as out:
    yaml.dump(bites, out, encoding='UTF-8', allow_unicode=True)

with open("bites.yaml") as bitesFile:
    bites = yaml.safe_load(bitesFile)

print(bites)
