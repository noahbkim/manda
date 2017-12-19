import json
import csv
import numpy
from concurrent.futures import ThreadPoolExecutor


def m(x, y):
    return (x[0] - y[0])**2 + (x[1] - y[1])**2


def flatten(x):
    if isinstance(x, list):
        return [a for i in x for a in flatten(i)]
    return [x]
    

def simplify(geography, voting):
    """Convert a topojson file to a simplified format."""

    out = []

    # Load the topojson file
    with open(geography) as file:
        geo = json.load(file)
    state = tuple(geo["objects"].keys())[0]

    # Load the CSV file with voting data
    votes = {}
    with open(voting) as file:
        reader = csv.reader(file)
        next(reader)  # Skip headers
        next(reader)
        for geoid, d2016, r2016, *_ in reader:
            votes[int(geoid)] = [int(d2016), int(r2016)]

    total = 0
    missing = 0

    for precinct in geo["objects"][state]["geometries"]:
        geoid = int(precinct["properties"]["GEOID10"])
        total += 1
        
        if geoid not in votes:
            print("Missing voting data for precinct %i" % geoid)
            votes[geoid] = [0, 0]
            missing += 1

        out.append({
            "id": geoid,
            "name": precinct["properties"]["NAME10"],
            "arcs": flatten(precinct["arcs"]),
            "population": precinct["properties"]["TOTAL_POPU"],
            "d2016": votes[geoid][0],
            "r2016": votes[geoid][1]})

    print("Missing voting data for %i precincts" % missing)
    print("Loaded %i precincts total" % total)

    with open("data/simple.json", "w") as file:
        json.dump(out, file, indent=2)
        

def adjacent(geography):
    """Load adjacent GeoID's."""

    # Load district polygons
    with open(geography) as file:
        data = json.load(file)
    precincts = []
    for precinct in data["features"]:
        geometry = precinct["geometry"]
        if geometry["type"] == "Polygon":
            coordinates = sum(geometry["coordinates"], [])
        elif geometry["type"] == "MultiPolygon":
            coordinates = sum(sum(geometry["coordinates"], []), [])
        precincts.append({
            "id": precinct["properties"]["GEOID10"],
            "coordinates": coordinates})

    count = len(precincts)
    adjacent = {precinct["id"]: [] for precinct in precincts}

    # Check adjacency
    def check(i, a, rest):
        print("%i/%i %f" % (i, count, i/count))
        for b in rest:
            close = False
            for c in a["coordinates"]:
                for d in b["coordinates"]:
                    if m(c, d) < 1e-2:
                        close = True
            if close:
                adjacent[a["id"]].append(b["id"])
                adjacent[b["id"]].append(a["id"])

    executor = ThreadPoolExecutor()
    for i, precinct in enumerate(precincts[:-1]):
        #check(precinct, precincts[i+1:])
        executor.submit(check, i, precinct, precincts[i+1:])
    executor.shutdown(wait=True)

    with open("data/adjacent.json", "w") as file:
        json.dump(adjacent, file, indent=2)
