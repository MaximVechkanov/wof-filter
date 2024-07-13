#!/bin/python3

from __future__ import annotations
import argparse
import yaml
from enum import Enum
import my_utilities
import os
# from pprint import pprint


LocationType = tuple[str, str]
LocBiteTimeTuple = tuple[str, str, str]

Database = tuple[dict[str], set[str], set[LocationType]] # fishes, bites, locations
minDepthStep = 0.01
kMaxDepth = 1000
minFloatDepth = 0.4
fish_db_dir = 'fish_db'
bottom_level_width = 1.

global_loc_db = dict()

time_name = {
    "у": "утро",
    "д": "день",
    "в": "вечер",
    "н": "ночь"
}

bottomType = {
    "only": "Только дно",
    "near": "Придонный слой",
    "nope": "Не со дна"
}

class EdgeType(Enum):
    LOW = 1
    HIGH = 2

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

class LayerType(Enum):
    ALL = 0
    UPPER = 1
    LOWER = 2
    BOTTOM = 3

    def __str__(self):
        match(self):
            case LayerType.ALL: return "Все слои"
            case LayerType.UPPER: return "Верхний слой"
            case LayerType.LOWER: return "Придонный слой"
            case LayerType.BOTTOM: return "Дно"
    
    def __lt__(self, other):
        return self.value < other.value

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
        return f"{float(self.low):.2f} - {float(self.high):.2f}"
        
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
    
    def __repr__(self) -> str:
        return str(self)

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

    def __repr__(self) -> str:
        return str(self)

def get_max_depth(locDb, location: LocationType) -> float:
    return locDb[location[0]][location[1]]['max-depth']

def get_min_depth(locDb, location: LocationType) -> float:
    return locDb[location[0]][location[1]]['min-depth']

def check_database(fishDb: dict, bites: list, locations: list) -> bool:
    for fishName in fishDb:

        if len(fishDb[fishName]['depth']) != 2:
            print("Ошибка: Некорректно указана глубина для рыбы '{}'".format(fishName))
            return False

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

        for location in fishLocs:
            if not location in locations:
                print("Ошибка: Локация '{}', указанная для рыбы '{}' не найдена в списке локаций!".format(location, fishName))
                return False
    return True

def parse_locations(locDb: dict, fishDb: dict) -> list[LocationType]:
    locations = []

    for water in locDb:
        for loc in locDb[water]:
            fishlist = locDb[water][loc]['fish']

            locationAsTuple = (water, loc)

            locations.append(locationAsTuple)

            for fishName in fishlist:
                if fishName in fishDb:
                    fishDb[fishName].setdefault('locs', list()).append(locationAsTuple)

    return locations

def load_fish_database() -> dict:
    result = dict()

    for filename in os.listdir(fish_db_dir):
        fullFileName = os.path.join(fish_db_dir, filename)

        # print(filename, ' ', fullFileName)

        with open(fullFileName) as file:
            newData = yaml.safe_load(file)

            if newData is not None:
                result.update(newData)

    return result

def load_database() -> Database:
    with open('bites.yaml') as bFile, open('locations_new.yaml') as locFile:
        fishDb = load_fish_database()

        print(f"Num fishes in database: {len(fishDb)}")

        bites = yaml.safe_load(bFile)
        locDb = yaml.safe_load(locFile)

        global global_loc_db
        global_loc_db = locDb

        locations: list[LocationType] = parse_locations(locDb, fishDb)

        # pprint(locations)

        if not check_database(fishDb, bites, locations):
            raise RuntimeError("Database currupted")
        
    return (fishDb, set(bites), set(locations))


def html_write_row(file, values: list[str]) -> None:
    file.write("<tr>\n")
    for idx, item in enumerate(values):
        file.write("  <td")
        if (idx == len(values) - 1):
            file.write(' valign="top"')
        file.write(">" + str(item) + "</td>" + '\n')
    file.write("</tr>\n")


def html_table_write_header(file, values: list[str]) -> None:
    file.write("<tr>\n")
    for idx, item in enumerate(values):
        file.write("  <th onclick=\"sortTable({})\">".format(idx) + str(item) + "</th>" + '\n')
    file.write("</tr>\n")


def to_html_list(items, ordered: bool = False) -> str:
    pre = list(items)
    pre.sort()
    
    result = ""
    if ordered:
        result += '<ol>\n'
    else:
        result += '<ul>\n'

    for item in pre:
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

def write_html_header(htmlFile, title):
    htmlFile.write('<!DOCTYPE html>\n')
    htmlFile.write('<html>\n')
    htmlFile.write('<head>\n')
    htmlFile.write(f'  <title>{title}</title>\n')
    htmlFile.write('\n')
    html_embed_styles(htmlFile)
    htmlFile.write('</head>\n')


def merge_by_daytime(results) -> dict:
    mergedTime = dict()

    for resKey in results:
        fishes = results[resKey]
        key = (resKey.loc, resKey.bite, resKey.depth, fishes)
        # print(res)
        # print(hash(key))

        if key in mergedTime:
            mergedTime[key].append(resKey.time)
        else:
            mergedTime[key] = [resKey.time]

    return mergedTime


def merge_by_bite(results) -> dict:
    merged = dict()

    for resKey in results:

        time = frozenset(results[resKey])
        loc, bite, depth, fishes = resKey
        key = (loc, time, depth, fishes)

        if key not in merged:
            merged[key] = [bite]
        else:
            merged[key].append(bite)

    return merged

def print_results(title: str | None, results: dict, fishDb: dict, maxBycatch: int | None):

    if maxBycatch is None:
        maxBycatch = 1000

    if title is None:
        title = "Search results table"

    with open('result.html', 'w', encoding = 'utf-16') as htmlFile:
        write_html_header(htmlFile, title)

        htmlFile.write('\n<body>\n')
        htmlFile.write('<table id="results_table">\n')

        html_table_write_header(htmlFile, ['Локация', 'Время', 'Макс. глубина', 'Слой', 'Глубина', 'Наживки', 'Рыбы', 'Кол-во рыб', 'Управление'])

        for resKey in results:

            loc, time, depth, bitesSet, layer = resKey

            fishes = results[resKey]
            bites = list(bitesSet)
            bites.sort()

            if len(fishes) > (maxBycatch + 1):
                continue

            if depth.high < minFloatDepth:
                continue

            fishes.sort()

            # for idx, fishName in enumerate(fishes):
            #     bottomRelation = fishDb[fishName].get('bottom')
            #     if bottomRelation != None:
            #         fishes[idx] = f"{fishName} ({bottomType[bottomRelation]})"

            fishesStr = to_html_list(fishes)
            bitesStr = to_html_list(bites)

            if type(layer) is LayerType:
                layerStr = str(layer)
            else:
                layerStr = to_html_list(layer)


            # html_write_row(htmlFile, [location_name_from_tuple(res.loc), res.bite, time_name[res.time], str(res.depth), len(fishes), fishesStr])
            html_write_row(htmlFile, [
                location_name_from_tuple(loc),
                create_html_list_from_time_set(time),
                get_max_depth(global_loc_db, loc),
                layerStr,
                str(depth),
                bitesStr,
                fishesStr,
                len(fishes),
                '<button onclick="removeRow(this)">Удалить</button>'])

        htmlFile.write("</table>\n")
        html_embed_scripts(htmlFile)
        htmlFile.write("</body>\n")
        htmlFile.write("</html>\n")

def find_in_location(location: LocationType, name: str):
    return (name in location[0]) or (location[1] == name)

def can_catch_in_layer(bottomRelation: str | None, layer: LayerType) -> bool:
    if bottomRelation is None:
        return True
    
    if layer == LayerType.ALL:
        return True
    
    if bottomRelation == "nope":
        if layer == LayerType.BOTTOM:
            return False
        else:
            return True
    elif bottomRelation == "only":
        if layer == LayerType.BOTTOM:
            return True
        else:
            return False
    elif bottomRelation == "near":
        if layer == LayerType.UPPER:
            return False
        else:
            return True

def split_by_layer(merged: dict, fishDb: dict):
    
    results = dict()
    
    for key in merged:
        loc, time, depth, fishes = key

        hasLayerDiff = False
        for f in fishes:
            if fishDb[f].get('bottom') is not None:
                hasLayerDiff = True

        if not hasLayerDiff:
            newKey = (loc, time, depth, frozenset(merged[key]), LayerType.ALL)
            results[newKey] = fishes.copy()
        else:

            possibleLayers = list[LayerType]()
            minD = get_min_depth(global_loc_db, loc)
            maxD = get_max_depth(global_loc_db, loc)

            if depth.low < (maxD - bottom_level_width):
                possibleLayers.append(LayerType.UPPER)

            if depth.high > minD:
                possibleLayers.append(LayerType.BOTTOM)

            if depth.high >= (minD - bottom_level_width):
                possibleLayers.append(LayerType.LOWER)

            for layer in possibleLayers:

                newKey = (loc, time, depth, frozenset(merged[key]), layer)

                for f in fishes:
                    if can_catch_in_layer(fishDb[f].get('bottom'), layer):
                        results.setdefault(newKey, list()).append(f)
    
    merged = dict()
    for resKey in results:
        loc, time, depth, bitesSet, layer = resKey
        fishes = results[resKey]

        key = (loc, time, depth, frozenset(fishes), bitesSet)
        if key not in merged:
            merged[key] = [layer]
        else:
            merged[key].append(layer)

    results = dict()
    for oldKey in merged:
        loc, time, depth, fishes, bitesSet = oldKey
        layers = frozenset(merged[oldKey])
        newKey = (loc, time, depth, bitesSet, layers)
        results[newKey] = list(fishes)

    return results

def print_fish_in_db(fishDb: dict):
    l = list(fishDb.keys())
    l.sort()
    for idx, f in enumerate(l):
        print(f"{idx + 1}. {f}")

def main():
    parser = argparse.ArgumentParser(description='Parse fish database and provide filtered table for a fish/bite/location')
    parser.add_argument("-f", "--fish", help="Рыба")
    parser.add_argument("-b", "--bite", help="Наживка")
    parser.add_argument("-l", "--location", help="Локация")
    parser.add_argument("-m", "--maxbycatch", help="Максимальное количество рыб в прилове", type=int)
    parser.add_argument("-g", "--golden-bites", help="Включить золотые и редкие наживки", action="store_true")
    parser.add_argument("-p", "--paid-locations", help="Включить платные локации", action="store_true")
    args = parser.parse_args()

    # print(args.fish)

    (fishDb, bitesDb, locationsDb) = load_database()

    # print_fish_in_db(fishDb)
    # return 0

    if args.bite is not None and args.bite != '':
        if args.bite not in bitesDb:
            print("Ошибка: наживка '{}' не найдена в базе".format(args.bite))
            return 1
        else:
            bites = set([args.bite])
    elif not args.golden_bites:
        with open("golden_bites.yaml") as gbFile:
            goldenBites = yaml.safe_load(gbFile)
            bites = bitesDb.difference(goldenBites)
    else:
        bites = bitesDb
        
    
    time = set('удвн')
    depth = Depth(0, kMaxDepth)

    if args.location is not None and args.location != '':
        locs = set()
        for loc in locationsDb:
            if find_in_location(loc, args.location):
                locs.add(loc)
    elif not args.paid_locations:
        with open("paid_locations.yaml") as plFile:
            paidLocs = yaml.safe_load(plFile)
            locs = set()
        for loc in locationsDb:
            if loc[0] not in paidLocs:
                locs.add(loc)
    else:
        locs = locationsDb

    isFishSpecified = args.fish is not None and args.fish != ''

    if isFishSpecified:
        if (args.fish not in fishDb):
            print("Ошибка: рыба '{}' не найдена в базе".format(args.fish))
            return 1

        fishParams = fishDb[args.fish]
        bites = bites.intersection(fishParams['bites'])
        locs = locs.intersection(fishParams['locs'])
        time = time.intersection(list(fishParams['time']))
        # print(fishParams['depth'])
        depth = depth.intersection(Depth.fromList(fishParams['depth']))

    print(bites)
    print(locs)
    print(time)
    print(depth)

    initialResults = process(fishDb, bites, locs, time, depth)

    # print("Initial results length: " + str(len(initialResults)))

    
    cleanedUp = dict()

    for res in initialResults:
        if not isFishSpecified or args.fish in initialResults[res]:
            cleanedUp[res] = frozenset(initialResults[res])

    # print("Cleaned up results length: " + str(len(cleanedUp)))

    mergedByTime = merge_by_daytime(cleanedUp)

    # print("merge_by_daytime results length: " + str(len(meggedByTime)))

    merged = merge_by_bite(mergedByTime)

    print("Results length after all merges: " + str(len(merged)))

    layered = split_by_layer(merged, fishDb)

    if isFishSpecified:
        cleanedUp = {key: value for key, value in layered.items() if args.fish in value}
    else:
        cleanedUp = layered

    if args.fish is not None:
        title = args.fish
    elif args.location is not None:
        title = args.location
    else:
        title = "Search results table"

    print_results(title, cleanedUp, fishDb, args.maxbycatch)


def depths_from_edges(edges) -> list[Depth]:
    depths = []
    
    lowEdge = 0
    nesting = 0
    for d in edges:
        if d[1] == EdgeType.HIGH: # 2
            if nesting == 0:
                raise "WTF"
            if d[0] >= lowEdge:
                depths.append(Depth(lowEdge, d[0]))
                lowEdge = d[0] + minDepthStep
            nesting -= 1
        if d[1] == EdgeType.LOW: # 1
            if lowEdge != d[0] and nesting != 0:
                depths.append(Depth(lowEdge, d[0] - minDepthStep))
            lowEdge = d[0]
            nesting += 1

    return depths

def process(fishDb, bites, locs, time, depth: Depth) -> dict[CastParams, list[str]]: 
    intermediateResults = dict[LocBiteTimeTuple, list]()

    for loc in locs:
        # print("Location: {}".format(loc))
        for bite in bites:
            # print("  Bite: {}".format(bite))
            for t in time:
                # print("    Time: {}".format(time_name[t]))
                for fishName in fishDb:
                    fishParams: dict = fishDb[fishName]

                    if loc in fishParams['locs'] and bite in fishParams['bites'] and fishParams['time'].find(t) != -1 and depth.intersects(Depth.fromList(fishParams['depth'])):
                        key = LocBiteTimeTuple((loc, bite, t))

                        intermediateResults.setdefault(key, list[str]())
                        intermediateResults[key].append(fishName)

    results = dict()

    for key in intermediateResults:

        location = key[0]
        maxLocationDepth = get_max_depth(global_loc_db, location)

        high = depth.high if depth.high < maxLocationDepth else maxLocationDepth

        edges = [(depth.low, EdgeType.LOW), (high, EdgeType.HIGH)]


        for fishName in intermediateResults[key]:
            fishParams: dict = fishDb[fishName]
            
            fishDepth = Depth.fromList(fishParams['depth'])
            if (fishDepth.low > maxLocationDepth):
                continue
            
            if (fishDepth.high > maxLocationDepth):
                fishDepth.high = maxLocationDepth

            fishDepths = [(fishDepth.low, EdgeType.LOW), (fishDepth.high, EdgeType.HIGH)]

            for d in fishDepths:
                # if d not in edges:
                edges.append(d)

        edges.sort(key=lambda item: item[1])
        edges.sort(key=lambda item: item[0])

        # print(key)
        # print(edges)

        depths = depths_from_edges(edges)

        # print(depths)

        for d in depths:

            resKey = CastParams(key[0], key[1], key[2], d)

            for fishName in intermediateResults[key]:
                if d.intersects(Depth.fromList(fishDb[fishName]['depth'])):
                    results.setdefault(resKey, list[str]()).append(fishName)

    return results

if __name__ == "__main__":
    main()
