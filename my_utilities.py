import os
import yaml

LocationType = tuple[str, str]
Database = tuple[dict[str], set[str], set[LocationType], dict[str]] # fishes, bites, locations
fish_db_dir = 'fish_db'


def to_location_type(water: str, loc: str) -> LocationType:
    return (water, loc)


def location_name_from_strings(water: str, loc: str) -> str:
    return water + ": " + loc


def location_name_from_tuple(location: LocationType) -> str:
    return location_name_from_strings(location[0], location[1])


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

        locations: list[LocationType] = parse_locations(locDb, fishDb)

        # pprint(locations)

        if not check_database(fishDb, bites, locations):
            raise RuntimeError("Database currupted")
        
    return (fishDb, set(bites), set(locations), locDb)
