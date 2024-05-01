#!/bin/python3

import yaml
from pprint import pprint

with open("bites.yaml") as bitesFile:
    bites = yaml.safe_load(bitesFile)
    
# print(bites)

bites.sort()

with open("bites_sorted.yaml", "w") as out:
    yaml.dump(bites, out, encoding="utf-8")

# print(bites)
