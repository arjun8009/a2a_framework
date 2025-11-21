import geopandas as gpd
from pyproj import Transformer
from osdatahub import Extent
import os
import requests
import pandas as pd
import joblib
import pyproj
import warnings

warnings.filterwarnings("ignore")

BASE_PATH = r"C:\Users\ab1574\OneDrive - University of Exeter\Desktop\Ordnance_Survey\os_ngd_sample"


def query_address(filters:list, bbox:str, street_address:bool, filename:str):
    '''Utility function to query OS Data Hub Address API
    args:
        1. filters : list of filters to apply to the query
        2. bbox : NGD Extent to limit the query
        3. street_address : boolean to indicate if street address is required
    output:
        1. gdf : GeoDataFrame of the queried addresses'''
    
    if not street_address:
        paths = [ os.path.join(BASE_PATH,r"add_gb_builtaddress\add_gb_builtaddress.gpkg"),
                  os.path.join(BASE_PATH,r"add_gb_historicaddress\add_gb_historicaddress.gpkg"),
                  os.path.join(BASE_PATH,r"add_gb_nonaddressableobject\add_gb_nonaddressableobject.gpkg")
                  ]
    else:
        paths = [ os.path.join(BASE_PATH,r"add_gb_streetaddress\add_gb_streetaddress.gpkg")]
    
    gdf_list = [gpd.read_file(path) for path in paths]
    gdf = pd.concat(gdf_list, ignore_index=True)
    gdf = gdf.set_crs(epsg=27700)

    if bbox:
        entent_polygon_file = joblib.load(f"./artifacts/{bbox}.pkl")
        extent_polygon = entent_polygon_file.data.to_crs(epsg=27700)
        gdf = gpd.clip(gdf, extent_polygon)
    
    data_filtered = []
    if filters:
        for filter in filters:
            data_filtered.append(gdf[gdf["classificationdescription"] == filter])
    
    gdf = pd.concat(data_filtered, ignore_index=True)
    
    if not street_address:
        gdf.attrs = {"name":f"{filename}","description":"A geopandas dataframe containing address data with filters and bbox applied as per user request.","count":len(gdf)}
    else:
        gdf.attrs = {"name":f"{filename}","description":"A geopandas dataframe containing street address data with filters and bbox applied as per user request.","count":len(gdf)}

    if gdf.empty:
        return None

    return gdf

def query_buildings(filters:list, bbox:str, filename:str):
    '''Utility function to query OS Data Hub Building API
    args:
        1. filters : list of filters to apply to the query
        2. bbox : NGD Extent to limit the query
    output:
        1. gdf : GeoDataFrame of the queried buildings'''
    
    # Add paths to different building related geopackage files
    paths = [ os.path.join(BASE_PATH,r"bld_fts_buildings\bld_fts_buildings.gpkg"),
              os.path.join(BASE_PATH,r"bld_fts_buildingline\bld_fts_buildingline.gpkg"),
              os.path.join(BASE_PATH,r"bld_fts_buildingpart\bld_fts_buildingpart.gpkg")]
    
    # Read the geopackage files into geopandas dataframes
    gdf_list = [gpd.read_file(path) for path in paths]

    # Set the coordinate reference system to EPSG:27700 (British National Grid) nad apply bbox if provided
    if bbox:
        entent_polygon_file = joblib.load(f"./artifacts/{bbox}.pkl")
        extent_polygon = entent_polygon_file.data.to_crs(epsg=27700)
        gdf_list = [gpd.clip(gdf, extent_polygon) for gdf in gdf_list]
    
    # Apply filters to each of the dataframes and concatenate the results of multiple filters
    gdf_filtered = []
    for gdf in gdf_list:
        gdf_temp = []
        for filter in filters:
            gdf_temp.append(gdf[gdf["classificationdescription"] == filter])
        gdf_filtered.append(pd.concat(gdf_temp, ignore_index=True))

    gdf_list = [gdf for gdf in gdf_filtered if not gdf.empty]
    # Assign attributes to each GeoDataFrame
    gdf_attrs_list =[{"name":f"buildings_{filename}","description":"A geopandas dataframe containing building data with filters and bbox applied as per user request.","count":len(gdf_list[0])},
                     {"name":f"buildingline_{filename}","description":"A geopandas dataframe containing building line data with filters and bbox applied as per user request.","count":len(gdf_list[1])},
                     {"name":f"buildingpart_{filename}","description":"A geopandas dataframe containing building part data with filters and bbox applied as per user request.","count":len(gdf_list[2])}]
    
    # Return None if no dataframes are left after filtering
    for index, gdf in enumerate(gdf_list):
        gdf.attrs = gdf_attrs_list[index]
    
    if len(gdf_list) == 0:
        return None
    
    return gdf_list

def apply_extent_named_area(bbox:str, polygon_or_point:bool,filename:str):
    '''Utility function to apply bbox to named area data
    args:
        1. bbox : NGD Extent to limit the query
        2. polygon_or_point : boolean to indicate if bbox is a polygon or point
    output:
        1. gdf : GeoDataFrame of the queried named areas'''
    
    # Determine the path to the named area geopackage file based on whether polygon or point data is requested
    if polygon_or_point:
        path = os.path.join(BASE_PATH,r"gnm_fts_namedarea\gnm_fts_namedarea.gpkg")
    else:
        path = os.path.join(BASE_PATH,r"gnm_fts_namedarea\gnm_fts_namedareapoint.gpkg")

    # Read the geopackage file into a geopandas dataframe and set the coordinate reference system to EPSG:27700 (British National Grid) and apply bbox if provided
    gdf = gpd.read_file(path)
    gdf = gdf.set_crs(epsg=27700)

    if bbox:
        entent_polygon_file = joblib.load(f"./artifacts/{bbox}.pkl")
        extent_polygon = entent_polygon_file.data.to_crs(epsg=27700)
        gdf = gpd.clip(gdf, extent_polygon)
    
    gdf.attrs = {"name":f"{filename}","description":"A geopandas dataframe containing named area data with bbox applied as per user request.","count":len(gdf)}
    return gdf
