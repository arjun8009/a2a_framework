from osdatahub import NGD, PlacesAPI, Extent
import geopandas as gpd
from pyproj import Transformer
import os
import requests
import pandas as pd
import joblib
import pyproj

def lat_lon_to_northing_easting(lat, lon):
    # Define the projection: for UK use OSGB36
    '''Convert latitude and longitude to easting and northing
    Args:
    lat : float, latitude
    lon : float, longitude
    returns:
    tuple : easting and northing'''

    proj = pyproj.Proj('+init=epsg:27700')  # OSGB36 (British National Grid)
    easting, northing = proj(lon, lat)
    return easting, northing


def generate_extent_from_artifact(artifact_name):
    '''Utitlity function to load the artifact for the bbox and return extent
    args:
        1. artifact_name : The name of the artifact to calculate extent within
    output:
        1. extent : NGD Extent'''
    
    # loading the artifact and get the data
    artifact = joblib.load(f"./artifacts/{artifact_name}.pkl")
    area = artifact.data
    
    # converting geometry to same crs and getting bounds
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:27700")
    area_bbox = area['geometry'].total_bounds
    west, south = transformer.transform(area_bbox[1], area_bbox[0])
    east, north = transformer.transform(area_bbox[3], area_bbox[2])
    
    extent = Extent.from_bbox((west, south, east, north), crs="EPSG:27700")

    return extent



def get_filterable_features(collection):

    '''Get filterable categories for collections, In case it is address use the hardcoded categories of the places API
    Args:
    collection : str, the collection name
    returns:
    dict : The filterable categories for the collection'''


    if collection != "address":
    
        response = requests.get(
        f"https://api.os.uk/features/ngd/ofa/v1/collections/{collection}/queryables",
        headers={"key":"mquJppFlzV2SgEFGgrbPV1mGZeD8u33b"},
    )
        data = response.json()
        mapping = {}
        for i in data["properties"].keys():
            if data["properties"][i].get("enum") is not None:
                mapping[i] = data["properties"][i]["enum"]
            else:
                mapping[i] = "No categories here Enter a search string"
        
        return mapping["description"]
    else:
        print("In here")
        data_address = pd.read_csv("addressbase-product-classification-scheme.csv")
        filters = list(data_address["Class_Desc"])
        return  filters



def query_named_area(search_areas:list):

    '''
    Function to search named places using NGD names

    args:
        1. search_areas = A list of places to search
    output:
        1. A geopandas dataframe 
    '''

    all_results = []

    ngd = NGD(key=os.getenv("OSNDG_API_KEY"),collection="gnm-fts-namedarea-1")

    for i in search_areas:
        all_results.append(gpd.GeoDataFrame.from_features(ngd.query(max_results=50,cql_filter=f"name1_text='{i}'")["features"]))
    
    all_results = gpd.GeoDataFrame(pd.concat(all_results, ignore_index=True))
    
    return all_results



def query_address_and_buildings(address_or_building : bool, name_or_theme:list, bbox:str):
    
    '''
    Function to search places using NGD places or buildings. We can search specific address names or buildings with a theme. We can also search within an extent

    args:
        1. address_or_building = A bool value that indicates whether to search a particular address name or building theme
        2. name_or_theme : A list of searchable names or filterable themes
        3. bbox : An extent to srarch within. It is an artifact name and the utility function will make the extent from the artifact
    
    output:
        1. A geopandas dataframe
    '''    

    all_results = []

    # initialize all apis here
    places_api = PlacesAPI(key=os.getenv("OSNDG_API_KEY"))
    ngd = NGD(key=os.getenv("OSNDG_API_KEY"),collection="bld-fts-building-3")
    
    if bbox is not None:
        bbox = generate_extent_from_artifact(bbox)
        
    # if address begins
    if address_or_building:

        # check for extent
        if not bbox:
            # find search if not extent
            all_results = [gpd.GeoDataFrame.from_features(places_api.find(i)["features"]) for i in name_or_theme]
        
        else:
            # searching with specific terms is not supported within extent, search with logical codes but if we want to search specific things then codes dont matter so search within extent and let coding agent do its work
            all_results = [gpd.GeoDataFrame.from_features(places_api.query(extent=bbox,limit=1000)["features"])]
    else:

        if not bbox:
            # search using description filters
            all_results = [gpd.GeoDataFrame.from_features(ngd.query(cql_filter=f"description = {i}")["features"]) for i in name_or_theme]
        
        else:
            # search using description filters within extent. Later will link this to address using UPRN
            all_results = [gpd.GeoDataFrame.from_features(ngd.query(extent=bbox, cql_filter=f"description = {i}")["features"]) for i in name_or_theme]
    
    all_results = gpd.GeoDataFrame(pd.concat(all_results, ignore_index=True))
    return all_results
