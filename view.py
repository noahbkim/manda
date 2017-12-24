import tkinter as tk
import geojson
import json
import random



class Polygon:
    """A custom polygon implementation for precincts."""

    def __init__(self, *parts, flag=False):
        """Instantiate a new polygon, may have multiple parts."""

        self.flag = flag
        self.parts = parts

    def __iter__(self):
        """Iterate over the parts of the polygon."""

        return iter(self.parts)

    @classmethod
    def precinct(self, precinct, flag=False):
        """Return a polygon from a precinct."""

        parts = []
        if precinct.geometry.type == "Polygon":
            parts.append(precinct.geometry.coordinates[0])
        elif precinct.geometry.type == "MultiPolygon":
            for coordinates in precinct.geometry.coordinates:
                parts.append(coordinates[0])
        return Polygon(*parts, flag=flag)


class PolygonGroup:
    """A group of Polygons with bounds, centering, and transforms."""

    def __init__(self, *polygons):
        """Instantiate a new polygon group."""

        self.polygons = polygons
        self._box = None
        self._center = None

    @property
    def box(self):
        """Compute the bounding box of the group."""

        if self._box is None:
            left = float("inf")
            bottom = float("inf")
            right = float("-inf")
            top = float("-inf")
            for part in self.parts:
                for x, y in part:
                    left = min(x, left)
                    bottom = min(y, bottom)
                    right = max(x, right)
                    top = max(y, top)
            self._box = ((left, bottom), (right, top))
            
        return self._box

    @property
    def center(self):
        """Compute the center of the group."""

        (x1, y1), (x2, y2) = self.box
        return (x2 + x1) / 2, (y2 + y1) / 2

    @property
    def parts(self):
        """Get the parts of the polygons."""

        return sum(map(list, self.polygons), [])

    @property
    def flagged(self):
        """Get the flagged parts."""

        for polygon in self.polygons:
            for part in polygon:
                yield part, polygon.flag


class AdjacencyViewer:
    """A single canvas application."""

    def __init__(self, geography, adjacency):
        """Create a new application."""

        self.width = 700
        self.height = 700
        self.load(geography, adjacency)

    def load(self, geography, adjacency):
        """Load file data."""
            
        with open(geography) as file:
            self.geography = geojson.load(file)
        with open(adjacency) as file:
            self.adjacency = json.load(file)

    def build(self):
        """Build the graphical components."""

        self.root = tk.Tk()
        self.root.title("Adjacency Viewer")
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.X)
        self.geoid = tk.StringVar(self.root)
        self.entry = tk.Entry(self.frame, textvariable=self.geoid)
        self.entry.pack(side=tk.LEFT)
        self.button = tk.Button(self.frame)
        self.button.config(text="Random", command=self.view_random)
        self.button.pack(side=tk.RIGHT)
        self.canvas = tk.Canvas(self.root)
        self.canvas.config(width=self.width, height=self.height)
        self.canvas.pack(side=tk.BOTTOM)

    def view_random(self):
        """View a random precinct."""

        feature = random.choice(self.geography.features)
        self.view_precinct(feature.properties["GEOID10"])

    def get_precinct(self, geoid):
        """Get a precinct by its geographic ID."""

        for feature in self.geography.features:
            if feature.properties["GEOID10"] == geoid:
                return feature

    def view_precinct(self, geoid):
        """View a precinct by its geographic ID."""

        precinct = self.get_precinct(geoid)
        neighbors = list(map(self.get_precinct, self.adjacency[geoid]))
        group = PolygonGroup(
            Polygon.precinct(precinct, flag=True),
            *list(map(Polygon.precinct, neighbors)))
        self.draw_group(group)
        self.geoid.set(geoid)

    def draw_group(self, group):
        """Draw a precinct."""

        self.canvas.delete("all")

        bl, tr = group.box
        w = tr[0] - bl[0]
        h = tr[1] - bl[1]
        s = (self.width - 100) / w if w > h else (self.height - 100) / h
        cx, cy = group.center

        for part, flag in group.flagged:
            coordinates = []
            for x, y in part:
                nx = (x - cx) * s + self.width / 2
                ny = (y - cy) * s + self.height / 2
                coordinates.append((nx, self.height - ny))
            self.canvas.create_polygon(
                *coordinates,
                fill="red" if flag else "black")

    def run(self):
        """Run the application."""

        self.build()
        self.view_precinct("1815300010")
        self.root.mainloop()


def view_adjacent(geography, adjacency):
    """View each district and adjacent districts."""

    a = AdjacencyViewer(geography, adjacency)
    a.run()


view_adjacent("derived/indiana.geojson", "derived/indiana.adjacency.json")
    
