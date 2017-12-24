import tkinter as tk
import geojson
import json



class AdjacencyViewer:
    """A single canvas application."""

    def __init__(self, geography, adjacency):
        """Create a new application."""

        self.load(geography, adjacency)

    def load(self, geography, adjacency):
        """Load file data."""
            
        with open(geography) as file:
            self.geography = geojson.load(file)
        with open(adjacency) as file:
            self.adjacent = json.load(file)

    def build(self):
        """Build the graphical components."""

        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root)
        self.canvas.config(width=800, height=600)
        self.canvas.pack()

    def get_precinct(self, geoid):
        """Get a precinct by its geographic ID."""

        for feature in self.geography.features:
            if feature.properties["GEOID10"] == geoid:
                return feature

    def view_precinct(self, geoid):
        """View a precinct by its geographic ID."""

        precinct = self.get_precinct(geoid)
        neighbors = list(map(self.get_precinct, self.adjacency[geoid]))

    def draw_precinct(self, precinct):
        """Draw a precinct."""

        if precinct.geometry.type == "Polygon":
            self.canvas.create_polygon(*precinct.geometry.coordinates[0])
        elif precinct.geometry.type == "MultiPolygon":
            for coordinates in precinct.geometry.coordinates:
                self.canvas.create_polygon(*coordinates[0])

    def run(self):
        """Run the application."""

        self.build()
        self.root.mainloop()


def view_adjacent(geography, adjacency):
    """View each district and adjacent districts."""


    
