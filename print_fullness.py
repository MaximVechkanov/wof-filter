#!/bin/python3
from my_utilities import *
import html_utils as html

def main():
    (fishDb, bitesDb, locationsSet, locationsRaw) = load_database()
    
    
    with open('statistics.html', 'w', encoding = 'utf-16') as htmlFile:
        html.write_html_header(htmlFile, 'Fullness of database')

        htmlFile.write('\n<body>\n')
        htmlFile.write('<table id="results_table">\n')

        html.html_table_write_header(htmlFile, ['Локация', 'Заполнено', 'Рыб отсутствует', 'Недостающие рыбы'])
        
        for water, locations in locationsRaw.items():
            absent_fish = list()
            all_water_fish = set()
            
            for loc, locInfo in locations.items():
                all_water_fish.update(locInfo['fish'])
                
            for fish in all_water_fish:
                if fish not in fishDb:
                    absent_fish.append(fish)
                
            html.html_write_row(htmlFile, [
                water,
                f'{len(all_water_fish) - len(absent_fish)}/{len(all_water_fish)}',
                len(absent_fish),
                html.to_html_list(absent_fish, True),
                ])
                
        htmlFile.write("</table>\n")
        html.html_embed_scripts(htmlFile)
        htmlFile.write("</body>\n")
        htmlFile.write("</html>\n")
            
        
    # for fish, fishInfo in fishDb.items():
    #     print(fishInfo['locs'])
    #     return


if __name__ == "__main__":
    main()