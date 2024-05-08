import yaml
import os

path_prefix = 'forum/locations/'
water_name_label = ' - Водоемы'

fish_list_label = 'Список рыбы по локациям:'
fish_list_label_len = len(fish_list_label)
fish_list = 'style="display:none;">'
loc_list_label = 'Скрытый текст'
loc_list_label_len = len(loc_list_label)

def main():
    
    directory = os.fsencode(path_prefix)

    startIdx = 0
    
    for fileName in os.listdir(directory):
        with open(path_prefix + fileName.decode()) as f:
            content = f.read()
            
            pos2 = content.find(water_name_label)
            pos1 = content.rfind('\n', 0, pos2)
            # print(pos1)
            # print(pos2)
            water = content[pos1+1:pos2]

            print(fileName)
            print(water)

            # continue


            startIdx = content.find(fish_list_label, pos2) + fish_list_label_len
            veryLast = content.find('\n\n\n', startIdx)

            allLists = content[startIdx:veryLast]
            # print(allLists)

            # continue

            while (pos := content.find('Скрытый текст', startIdx)) != -1:
                endPos = content.find('\n\n', pos)

                locName = content[startIdx:pos].strip()

                print(locName)

                fishList = content[pos + loc_list_label_len + 2:endPos]
                

                # print(fishList)
                print('')

                fish = fishList.split('\n')
                print(fish)

                startIdx = endPos


    return 0

if __name__ == "__main__":
    main()
