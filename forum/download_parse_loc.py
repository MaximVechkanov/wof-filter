#!/bin/python3

import urllib.request
import sys
from bs4 import *
from string import printable

removed_chars = ['\xa0']

fish_list_begin_label = '<div class="bbc_spoiler_wrapper"><div class="bbc_spoiler_content" style="display:none;">'


def main():
    url = sys.argv[1]

    if url.find('http') != -1:
        rsp = urllib.request.urlopen(url)
        soup = BeautifulSoup(rsp.read(), "html.parser")
    else:
        with open(url) as file:
            soup = BeautifulSoup(file.read(), "html.parser")
    
    body: str = soup.body.decode()

    title = soup.title.decode()

    waterName = title[len('<title>'):title.find(' - ')]

    print(waterName)

    # print(type(body))
    # print(body)
    # return 1

    loc_pic_pos = body.find('href="https://yapx.ru')
    sub = body[loc_pic_pos:]

    if (mainListStart := sub.find('Список рыбы по локациям')) == -1:
        mainListStart = sub.find('Список рыб по локациям')

    sub = sub[mainListStart:]

    tail_pos = sub.find('<div class="post_controls"')

    sub = sub[:tail_pos]

    # print(sub)

    locs = sub.split('<strong>')
    del locs[0]

    locations = dict()

    for idx, l in enumerate(locs):
        if l.find('Сообщение отредактировал') != -1:
            continue
        # print(idx)
        # print(l)
        # print('\n')
        rawLocName = l[:l.find('</strong>')]
        locName = ''.join(char for char in rawLocName if char not in removed_chars)

        soup = BeautifulSoup(locName, "html.parser")
        locName = soup.get_text()

        print(f"  {locName}")

        locations[locName] = list()

        listBegin = l[l.find(fish_list_begin_label) + len(fish_list_begin_label):]
        fishOnly = listBegin.replace('<div>', '').replace('</div>', '').replace('</p>', '').replace('<p>', '<br/>').replace('<br>', '')

        # print(fishOnly)

        fishes = fishOnly.split('<br/>')

        for f in fishes:

            if f.find('span') != -1:
                continue

            fishName = f.replace('\n', '')

            if (fishName != ''):
                locations[locName].append(fishName)


    # fileName = url[url.find('topic/')+5:].strip('/') + '.yaml'
    fileName = waterName + '.yaml'

    with open('locations_db' + '/' + fileName, 'w', encoding='utf-8') as file:
        file.write(f"{waterName}:\n")
        for water in locations:
            file.write(f"  {water}:\n")
            for loc in locations[water]:
                file.write(f"    - {loc}\n")


if __name__ == "__main__":
    main()
