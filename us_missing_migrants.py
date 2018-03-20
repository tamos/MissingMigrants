#! path/to/missing_migrants/bin/python


import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from bokeh.io import show
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper
from bokeh.palettes import Viridis6 as palette
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.sampledata.us_counties import data as counties
from bokeh.models import GeoJSONDataSource

palette.reverse()


# Hats off to : https://medium.com/@bobhaffner/spatial-joins-in-geopandas-c5e916a763f3

file_path  = "MissingMigrants-Global-2018-03-19T22-10-39.csv"

def load_migrant_data(file_path):
    df = pd.read_csv(file_path, usecols = ["Location Coordinates", "Total Dead and Missing",
                                "Reported Date"],
                     dtype = {"Location Coordinates": str,
                              "Total Dead and Missing": int,
                                "Reported Date": str})
    split_out = lambda k: k.split(", ")
    split_list =  list(map(split_out, df["Location Coordinates"]))
    x  = []
    y = []
    for i in split_list:
        x.append(i[0])
        y.append(i[1])
    df["lat"] = [float(i) for i in x]
    df["lon"] = [float(i) for i in y]
    return df

def make_migrant_points(file_path):
    migrant_fatal = load_migrant_data(file_path)
    point_list = []
    label_list = []
    for i in migrant_fatal.iterrows():
        point_list.append(Point(i[1]["lat"], i[1]["lon"]))
        label_list.append(i[1]["Total Dead and Missing"])
    return point_list, label_list

def get_migrant_df(file_path):
    points, labels = make_migrant_points(file_path)
    migrant_df =  gpd.GeoDataFrame()
    migrant_df['geometry'] = points
    migrant_df['toll'] = labels
    return migrant_df


def make_county_polygons(counties):
    poly_list = []
    label_list = []
    id_list = []
    for i, j in counties.items():
        val_dict = j
        lats = [r for r in val_dict['lats']]
        lons = [k for k in val_dict['lons']]
        temp_poly = Polygon([[lats[t], lons[t]] for t in range(len(lats))])
        poly_list.append(temp_poly)
        label_list.append(val_dict['name'])
        id_list.append(i)
    return poly_list, label_list, id_list

def get_county_df(county_poly, labels, ids):
    county_df =  gpd.GeoDataFrame()
    county_df['geometry'] = county_poly
    county_df['names'] = labels
    county_df['id'] = ids
    return county_df


def join_county_migrant(county_df, migrant_df):
    return gpd.sjoin(migrant_df, county_df, op= 'within', how = 'inner')

def plot_counties(county_poly):
    geo_source = GeoJSONDataSource(geojson=county_poly)
    p = figure(
    title="Texas Unemployment, 2009", tools=TOOLS,
    x_axis_location=None, y_axis_location=None)
    p.patches('x', 'y', source = geo_source)
    show(p)
                            


def go():
    TOOLS = "pan,wheel_zoom,reset,hover,save"
    
    county_poly, labels, ids = make_county_polygons(counties)
    county_df = get_county_df(county_poly, labels, ids)
    migrant_df = get_migrant_df(file_path)
    joined = join_county_migrant(county_df, migrant_df)
    plot_counties(county_poly)
    
    
if __name__ == "__main__":
    
    go()
