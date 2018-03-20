
#! path/to/missing_migrants/bin/python

from bokeh.io import show, output_file
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LogColorMapper
)
from bokeh.palettes import Viridis6 as palette
from bokeh.plotting import figure

from bokeh.sampledata.us_counties import data as counties

import pandas as pd
from us_missing_migrants_preprocess import preprocess

def reduce_by_id(joined):
    results = {}
    for i in joined.itertuples():
        if i.id not in results:
            results[i.id] = i.toll
        else:
            results[i.id] += i.toll
    return results # we need the dictionary for the next part


def get_missing_migrant_data():
    joined = preprocess()
    return reduce_by_id(joined)

missing = get_missing_migrant_data()

# Below is borrowed from Bokeh Documentation with modification

palette.reverse()

exclusion = ["hi", "ak"] # get rid of hawai and alaska for ease of projection
inclusion = ["az", "ca", "fl", "la", "nm", "tx","ga", "al", "ms"] # state we want to see

counties = { code: county for code,
             county in counties.items() if county["state"] in inclusion}

county_xs = [county["lons"] for county in counties.values()]
county_ys = [county["lats"] for county in counties.values()]

county_names = [county['detailed name'] for county in counties.values()]
county_rates = [missing[county_id] for county_id in counties]
color_mapper = LogColorMapper(palette=palette)

source = ColumnDataSource(data=dict(
    x=county_xs,
    y=county_ys,
    name=county_names,
    rate=county_rates,
))

TOOLS = "pan,wheel_zoom,reset,hover,save"

p = figure(
    title="Missing Migrants in the US", tools=TOOLS,
    x_axis_location=None, y_axis_location=None
)
p.grid.grid_line_color = None

p.patches('x', 'y', source=source,
          fill_color={'field': 'rate', 'transform': color_mapper},
          fill_alpha=0.9, line_color="white", line_width=0.5)

hover = p.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [
    ("Name", "@name"),
    ("Number of Migrant Fatalities", "@rate"),
]
output_file("missing_migrants.html")
show(p)


