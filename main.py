#!/bin/python3

from __future__ import annotations

import argparse
import yaml
import csv
from pprint import pprint

Database = tuple[dict[str], set[str], set[str]]
minDepthStep = 0.01

time_name = {
    "у": "утро",
    "д": "день",
    "в": "вечер",
    "н": "ночь"
}

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

class CastParams:
    loc: str
    bite: str
    time: str
    depth: Depth

    def __init__(self, location, bite, time, depth) -> None:
        self.loc = location
        self.bite =  bite
        self.time = time
        self.depth = depth

def location_name(water: str, loc: str) -> str:
    return water + ": " + loc

def check_database(fishDb: dict, bites: list, locations: list) -> bool:
    for fishName in fishDb:
        fishBites = fishDb[fishName]['bites']

        if fishBites is None:
            print("Ошибка: Наживки не указаны для рыбы '{}'".format(fishName))
            return False

        # print(fishBites)
        # print(type(fishBites))

        for fb in fishBites:
            if not fb in bites:
                print("Ошибка: Наживка '{}', указанная для рыбы '{}' не найдена в списке наживок!".format(fb, fishName))
                return False
        
        fishLocs = fishDb[fishName]['locs']
        if fishLocs is None:
            print("Ошибка: локации не указаны для рыбы '{}'".format(fishName))
            return False

        for water in fishLocs:
            for loc in fishLocs[water]:
                if not location_name(water, loc) in locations:
                    print("Ошибка: Локация '{}', указанная для рыбы '{}' не найдена в списке локаций!".format(loc, fishName))
                    return False

    return True

def loc_list_from_dict(locDb: dict) -> list[str]:
    locations = []

    for water in locDb:
        for loc in locDb[water]:
            locations.append(location_name(water, loc))
    return locations

def load_database() -> Database:
    with open('fish.yaml') as fFile, open('bites.yaml') as bFile, open('locations.yaml') as locFile:
        fish = yaml.safe_load(fFile)
        bites = yaml.safe_load(bFile)
        locDb = yaml.safe_load(locFile)

        locations = loc_list_from_dict(locDb)

        # print(locations)

        if not check_database(fish, bites, locations):
            raise "Database currupted"
        
        return (fish, set(bites), set(locations))

def main():
    parser = argparse.ArgumentParser(description='Parse fish database and provide filtered table for a fish/bite/location')
    parser.add_argument("-f", "--fish", help="Рыба")
    parser.add_argument("-b", "--bite", help="Наживка")
    parser.add_argument("-l", "--location", help="Локация")
    args = parser.parse_args()

    # print(args.fish)

    (fishDb, bitesDb, locationsDb) = load_database()

    if args.bite is not None:
        bites = set([args.bite])
    else:
        bites = bitesDb
        
    locs = locationsDb
    time = set(list('удвн'))
    depth = Depth(0, 1000)

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

    results = dict[CastParams, list[str]]()

    for loc in locs:
        for bite in bites:
            for t in time:

                depths = [depth]

                for fishName in fishDb:
                    
                    fishParams = fishDb[fishName]
                    
                    if loc in loc_list_from_dict(fishParams['locs']) and bite in fishParams['bites'] and t in list(fishParams['time']):
                        # check depth
                        fDepth = Depth.fromList(fishParams['depth'])

                        # print("Match")

                        for d in depths:
                            if d.intersects(fDepth):

                                common = d.intersection(fDepth)

                                key = CastParams(loc, bite, t, common)

                                if (common != d):
                                    newSet = d.split(common)

                                    if key in results:
                                        fishes = results[key]

                                        del results[key]

                                        for newDepths in newSet:
                                            results[key] = fishes

                                # print("Match 2")


                                if key in results and results[key] is not None:
                                    results[key].append(fishName)
                                else:
                                    results[key] = [fishName]


    with open('result.csv', 'w', newline = '', encoding='utf-8') as csvFile:
        writer = csv.writer(csvFile, delimiter=',')
        writer.writerow(['Водоём', 'Наживка', 'Время', 'Глубина', 'Рыбы'])

        for res in results:
            writer.writerow([res.loc, res.bite, time_name[res.time], str(res.depth), results[res]])

if __name__ == "__main__":
    main()
