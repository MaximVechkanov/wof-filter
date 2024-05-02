#!/bin/python3

import yaml

res = ''

with open('locations.yaml') as lFile:
    locs = yaml.safe_load(lFile)

    # print (locs)
    # print(type(locs))

    for pond in locs:
        # print(pond, ':', locs[pond])
        for loc in locs[pond]:
            res += '{}: {}'.format(pond, loc) + '\n'
        # print(loc.key, loc.value)

with open('locs_all.txt', 'w') as lFile:
    lFile.write(res)
