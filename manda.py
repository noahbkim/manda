import shapefile
import geojson
import json
import os

from shapely.geometry import polygon


def get_file_name(path):
    """Get the name of a file with no extension."""

    return os.path.splitext(os.path.split(source)[1])[0]


def get_write_path(destination, name):
    """Get a write path using default file name if given a directory."""

    if os.path.isdir(destination):
        return os.path.join(destination, name)
    return destination


def shape_to_geojson(shape, destination="derived/"):
    """Convert a shape file to GeoJSON."""

    reader = shapefile.Reader(shape)
    fields = reader.fields[1:]
    names = [field[0] for field in fields]
    buffer = []

    for record in reader.shapeRecords():
        properties = dict(zip(names, record.record))
        geometry = record.shape.__geo_interface__
        buffer.append(geojson.Feature(
            geometry=geometry,
            properties=properties))

    collection = geojson.FeatureCollection(buffer)

    name = get_file_name(shape) + ".geojson"
    with open(get_write_path(destination, name), "w") as write:
        geojson.dump(collection, write)


def compute_adjacent(geography, destination="derived/"):
    """Compute the adjacent precincts."""

    with open(geography) as file:
        data = geojson.load(file)

    polygons = []
    for i in range(len(data.features)):
        n = data[i].properties["GEOID10"]
        if data[i].geometry.type == "Polygon":
            p = polygon.Polygon(data[i].geometry.coordinates[0])
            polygons.append((p, n))
        elif data[i].geometry.type == "MultiPolygon":
            for coordinates in data[i].geometry.coordinates:
                p = polygon.Polygon(coordinates[0])
                polygons.append((p, n))
        
    t = len(polygons)

    adjacent = {n: [] for p, n in polygons}
    try:
        for i, (a, na) in enumerate(polygons[:-1]):
            print("%i/%i %f%%" % (i, t, i/t * 100))
            for (b, nb) in polygons[i+1:]:
                if a.intersects(b):
                    adjacent[na].append(nb)
                    adjacent[nb].append(na)
    except:
        print("cancelled at %i" % i)

    name = get_file_name(geography) + ".adjacency.json"
    with open(get_write_path(destination, name), "w") as file:
        json.dump(adjacent, file)

