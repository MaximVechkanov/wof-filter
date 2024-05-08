#!/bin/python3

from __future__ import annotations

import argparse
import yaml
# from pprint import pprint



LocationType = tuple[str, str]

Database = tuple[dict[str], set[str], set[LocationType]] # fishes, bites, locations
minDepthStep = 0.01
kMaxDepth = 100

time_name = {
    "у": "утро",
    "д": "день",
    "в": "вечер",
    "н": "ночь"
}



def to_location_type(water: str, loc: str) -> LocationType:
    return (water, loc)


def location_name_from_strings(water: str, loc: str) -> str:
    return water + ": " + loc


def location_name_from_tuple(location: LocationType) -> str:
    return location_name_from_strings(location[0], location[1])


def loc_list_to_str_list(locationsList: list[LocationType]) -> list[str]:
    res = []
    for item in locationsList:
        res.append(location_name_from_tuple(item))
    return res

class Depth:
    low: float
    high: float

    def __init__(self, low: float, high: float):
        self.low = low
        self.high = high

    def fromList(values: list[float]) -> Depth:
        return Depth(values[0], values[1])

    def intersects(self, other: Depth) -> bool:
        if (self.high < other.low):
            return False
        if (self.low > other.high):
            return False
        return True
    
    def intersection(self, other) -> Depth | None:
        if not self.intersects(other):
            return None
        return Depth(max(self.low, other.low), min(self.high, other.high))
        
    def __str__(self) -> str:
        return str(self.low) + '-' + str(self.high)
        
    def split(self, intersection: Depth) -> list[Depth]:
        result = [intersection]
        if (intersection.high != self.high):
            result.append(Depth(intersection.high + minDepthStep, self.high))
        
        if (intersection.low != self.low):
            result.append(Depth(self.low, intersection.low - minDepthStep))

        result.sort()
        return result
    
    def __eq__(self, other) -> bool:
        return self.low == other.low and self.high == other.high
    
    def __lt__(self, other) -> bool:
        return self.low < other.low
    
    def __hash__(self) -> int:
        return hash(self.low) + 1000 * hash(self.high)


class CastParams:
    loc: LocationType
    bite: str
    time: str
    depth: Depth

    def __init__(self, location, bite, time, depth) -> None:
        self.loc = location
        self.bite =  bite
        self.time = time
        self.depth = depth

    def __eq__(self, value: CastParams) -> bool:
        return self.loc == value.loc and self.bite == value.bite and self.time == value.time and self.depth == value.depth
    
    def __hash__(self) -> int:
        return hash(self.loc) * hash(self.bite) * hash(self.time) * hash(self.depth)
    
    def __str__(self) -> str:
        return "Loc: " + location_name_from_tuple(self.loc) + '\nBite: ' + self.bite + '\nTime: ' + time_name[self.time] + '\nDepth: ' + str(self.depth)


def check_database(fishDb: dict, bites: list, locations: list) -> bool:
    for fishName in fishDb:
        fishBites = fishDb[fishName].get('bites')

        if fishBites is None:
            print("Ошибка: Наживки не указаны для рыбы '{}'".format(fishName))
            return False

        # print(fishBites)
        # print(type(fishBites))

        for fb in fishBites:
            if not fb in bites:
                print("Ошибка: Наживка '{}', указанная для рыбы '{}' не найдена в списке наживок!".format(fb, fishName))
                return False
        
        fishLocs = fishDb[fishName].get('locs')
        if fishLocs is None:
            print("Ошибка: локации не указаны для рыбы '{}'".format(fishName))
            return False

        for water in fishLocs:
            for loc in fishLocs[water]:
                if not to_location_type(water, loc) in locations:
                    print("Ошибка: Локация '{}', указанная для рыбы '{}' не найдена в списке локаций!".format(loc, fishName))
                    return False
    return True


def loc_list_from_dict(locDb: dict) -> list[LocationType]:
    locations = []

    for water in locDb:
        for loc in locDb[water]:
            locations.append((water, loc))

    return locations


def load_database() -> Database:
    with open('fish.yaml') as fFile, open('bites.yaml') as bFile, open('locations.yaml') as locFile:
        fish = yaml.safe_load(fFile)
        bites = yaml.safe_load(bFile)
        locDb = yaml.safe_load(locFile)

        locations = loc_list_from_dict(locDb)

        # pprint(locations)

        if not check_database(fish, bites, locations):
            raise RuntimeError("Database currupted")
        
        return (fish, set(bites), set(locations))


def html_write_row(file, values: list[str]) -> None:
    file.write("<tr>\n")
    for item in values:
        file.write("  <td>" + str(item) + "</td>" + '\n')
    file.write("</tr>\n")


def html_table_write_header(file, values: list[str]) -> None:
    file.write("<tr>\n")
    for idx, item in enumerate(values):
        file.write("  <th onclick=\"sortTable({})\">".format(idx) + str(item) + "</th>" + '\n')
    file.write("</tr>\n")


def to_html_list(items, ordered: bool = False) -> str:
    result = ""
    if ordered:
        result += '<ol>\n'
    else:
        result += '<ul>\n'

    for item in items:
        result += '    <li>' + str(item) + '</li>\n'

    if ordered:
        result += '</ol>\n'
    else:
        result += '</ul>\n'
    
    return result


def create_html_list_from_time_set(timeset: set[str]) -> str:
    arr = []
    for t in timeset:
        arr.append(time_name[t])

    return to_html_list(arr)


def html_embed_scripts(htmlFile):
    htmlFile.write('<script type = "text/javascript">\n')
    with open('scripts.js') as sFile:
        htmlFile.write(sFile.read())
    htmlFile.write("</script>\n")

def html_embed_styles(htmlFile):
    htmlFile.write('  <style>\n')
    with open('styles.css') as sFile:
        htmlFile.write(sFile.read())
    htmlFile.write('  </style>\n')

def write_html_header(htmlFile):
    htmlFile.write('<!DOCTYPE html>\n')
    htmlFile.write('<html>\n')
    htmlFile.write('<head>\n')
    htmlFile.write('  <title>Results for searcher</title>\n')
    htmlFile.write('\n')
    html_embed_styles(htmlFile)
    htmlFile.write('</head>\n')


def merge_by_daytime(results) -> dict:
    mergedTime = dict()

    for res in results:
        key = (res.loc, res.bite, res.depth)
        # print(res)
        # print(hash(key))

        # if key in mergedTime:
        #     print(results[res])
        #     print(mergedTime[key])

        if key in mergedTime and results[res] == mergedTime[key][1]:
            mergedTime[key][0].add(res.time)
        else:
            mergedTime[key] = set(res.time), results[res]

    return mergedTime


def merge_by_location(results: dict[tuple, tuple]) -> dict[tuple, tuple]:
    merged = dict()

    for res in results:
        key = (res[1], res[2]) # bite, depth

        if key in merged and results[res][1] == merged[key][2] and results[res][0] == merged[key][1]:
            merged[key][0].append(res[0])
        else:
            merged[key] = ([res[0]], results[res][0], results[res][1])

    return merged


def merge_by_bite(results) -> dict:
    merged = dict[Depth]()

    for res in results:
        key = (res[0], res[2])

        if key in merged and results[res][0] == merged[key][1] and results[res][1] == merged[key][2]:
            merged[key][0].append(res[1])
        else:
            merged[key] = ([res[1]], results[res][0], results[res][1])

    return merged

def print_results(results, maxBycatch: int | None):

    if maxBycatch is None:
        maxBycatch = 1000

    with open('result.html', 'w', encoding = 'utf-16') as htmlFile:
        write_html_header(htmlFile)

        htmlFile.write('\n<body>\n')
        htmlFile.write('<table id="results_table">\n')

        html_table_write_header(htmlFile, ['Локации', 'Наживки', 'Время', 'Глубина', 'Кол-во рыб', 'Рыбы'])

        for res in results:

            if len(results[res][2]) > (maxBycatch + 1):
                continue

            bites, time, fishes = results[res]
            fishesStr = to_html_list(fishes)
            bitesStr = to_html_list(bites)

            # html_write_row(htmlFile, [location_name_from_tuple(res.loc), res.bite, time_name[res.time], str(res.depth), len(fishes), fishesStr])
            html_write_row(htmlFile, [location_name_from_tuple(res[0]), bitesStr, create_html_list_from_time_set(time), str(res[1]), len(fishes), fishesStr])


        htmlFile.write("</table>\n")
        html_embed_scripts(htmlFile)
        htmlFile.write("</body>\n")
        htmlFile.write("</html>\n")


def main():
    parser = argparse.ArgumentParser(description='Parse fish database and provide filtered table for a fish/bite/location')
    parser.add_argument("-f", "--fish", help="Рыба")
    parser.add_argument("-b", "--bite", help="Наживка")
    parser.add_argument("-l", "--location", help="Локация")
    parser.add_argument("--maxbycatch", help="Максимальное количество рыб в прилове", type=int)
    args = parser.parse_args()

    # print(args.fish)

    (fishDb, bitesDb, locationsDb) = load_database()

    if args.bite is not None and args.bite != '':
        if args.bite not in bitesDb:
            print("Ошибка: наживка '{}' не найдена в базе".format(args.bite))
            return 1
        else:
            bites = set([args.bite])
    else:
        bites = bitesDb
        
    locs = locationsDb
    time = set('удвн')
    depth = Depth(0, kMaxDepth)

    if args.fish is not None:
        if (args.fish not in fishDb):
            print("Ошибка: рыба '{}' не найдена в базе".format(args.fish))
            return 1

        fishParams = fishDb[args.fish]
        bites = bites.intersection(fishParams['bites'])
        locs = locs.intersection(loc_list_from_dict(fishParams['locs']))
        time = time.intersection(list(fishParams['time']))
        # print(fishParams['depth'])
        depth = depth.intersection(Depth.fromList(fishParams['depth']))

    print(bites)
    print(locs)
    print(time)
    print(depth)

    results = process(fishDb, bites, locs, time, depth)

    results = merge_by_daytime(results)

    # results: tuple(location, bite, depth) -> (time, fishes)

    merged = merge_by_bite(results)

    # results: tuple(location, depth) -> tuple(bite, time, fishes)

    print_results(merged, args.maxbycatch)


def process(fishDb, bites, locs, time, depth: Depth) -> dict[CastParams, list[str]]: 
    results = dict[CastParams, list[str]]()
    loopIndex = 0

    for loc in locs:
        # print("Location: {}".format(loc))
        for bite in bites:
            # print("  Bite: {}".format(bite))
            for t in time:
                # print("    Time: {}".format(time_name[t]))
                depths = [depth]
                newDepths = depths.copy()

                for fishName in fishDb:
                    loopIndex = loopIndex + 1

                    # print("      Fish: {}".format(fishName))
                    # print("*** LOOP INDEX: " + str(loopIndex) + " ***")
                    
                    fishParams = fishDb[fishName]
                    
                    if loc in loc_list_from_dict(fishParams['locs']) and bite in fishParams['bites'] and t in list(fishParams['time']):
                        # check depth
                        fDepth = Depth.fromList(fishParams['depth'])

                        # print("Match")

                        for d in depths:
                            if d.intersects(fDepth):
                                common = d.intersection(fDepth)

                                if common is None:
                                    continue

                                key = CastParams(loc, bite, t, common)
                                oldKey = CastParams(loc, bite, t, d)

                                if (common != d):
                                    newSet = d.split(common)
                                    newDepths.remove(d)
                                    newDepths.extend(newSet)

                                    # if (Depth(1, 1.49) in newSet) and bite == 'Мякиш хлеба':
                                    #     for k in results.keys():
                                    #         print(k)
                                        
                                    #     print('')
                                    #     print(oldKey)
                                    #     print(results[oldKey])

                                    if oldKey in results:
                                        fishes = results[oldKey].copy()
                                        del results[oldKey]

                                        # print(fishes)
                                    
                                        for newDepth in newSet:
                                            newKey = CastParams(loc, bite, t, newDepth)
                                            results[newKey] = fishes.copy()
                                            
                                # print("Match 2")

                                # print("--- BEFORE ---")

                                # for r in results:
                                #     print(r)
                                #     print(results[r])

                                results.setdefault(key, []).append(fishName)

                                # if key in results and results[key] is not None:
                                #     # print("appending")
                                #     # print(key)
                                #     # print(results[key])
                                #     # print(fishName)
                                #     results[key].append(fishName)
                                    
                                # else:
                                #     print("Adding")
                                #     print(key)
                                #     print(fishName)
                                #     results[key] = [fishName]
                                # print("--- AFTER ---")
                                # for r in results:
                                #     print(r)
                                #     print(results[r])

                        depths = newDepths.copy()
    return results

if __name__ == "__main__":
    main()
