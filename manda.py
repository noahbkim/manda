import json
import csv
import numpy


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
            "arcs": precinct["arcs"],
            "population": precinct["properties"]["TOTAL_POPU"],
            "d2016": votes[geoid][0],
            "r2016": votes[geoid][1]})

    print("Missing voting data for %i precincts" % missing)
    print("Loaded %i precincts total" % total)

    with open("data/out.json", "w") as file:
        json.dump(out, file, indent=2)
        
    
        
