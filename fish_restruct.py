#!/bin/python3

import yaml

new_folder = 'fish_db/'

# last included
def char_seq(first, last):
    for index in range(ord(first), ord(last) + 1):
        yield chr(index)

def main():
    with open('fish_new.yaml') as oldFile:
        oldData = yaml.safe_load(oldFile)

        for firstLetter in char_seq('А', 'Я'):
            # print(firstLetter)

            with open(new_folder + firstLetter + ".yaml", "w", encoding="utf-8") as newFile:
                data = dict()
                for fishName in oldData:
                    if fishName[0] == firstLetter:
                        data[fishName] = oldData[fishName]
                
                # yaml.dump(data, newFile, encoding='UTF-8', allow_unicode=True, default_flow_style=True)

                for fishName in data:
                    fishParams = data[fishName]
                    newFile.write(f"{fishName}:\n")
                    newFile.write(f"  time: {fishParams['time']}\n")
                    newFile.write(f"  depth: [{fishParams['depth'][0]}, {fishParams['depth'][1]}]\n")
                    newFile.write(f"  bites:\n")

                    bites = fishParams['bites']
                    for bite in bites:
                        newFile.write(f"    - {bite}\n")
                    newFile.write('\n')


if __name__ == '__main__':
    main()
