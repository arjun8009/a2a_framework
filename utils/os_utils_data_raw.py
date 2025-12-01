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
ARTIFACT_PATH = r"C:\Users\ab1574\OneDrive - University of Exeter\Desktop\Ordnance_Survey\artifacts"

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
        entent_polygon_file = joblib.load(os.path.join(ARTIFACT_PATH,f"{bbox}.pkl"))
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
        entent_polygon_file = joblib.load(os.path.join(ARTIFACT_PATH,f"{bbox}.pkl"))
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
        entent_polygon_file = joblib.load(os.path.join(ARTIFACT_PATH,f"{bbox}.pkl"))
        extent_polygon = entent_polygon_file.data.to_crs(epsg=27700)
        gdf = gpd.clip(gdf, extent_polygon)
    
    gdf.attrs = {"name":f"{filename}","description":"A geopandas dataframe containing named area data with bbox applied but no filters applied as per user request.","count":len(gdf)}
    return gdf


def query_water_features(bbox:str, filename:str):
    '''Utility function to query OS Data Hub Water API
    args:
        1. bbox : NGD Extent to limit the query
        2. filters : list of filters to apply to the query
        3. filename : name of the output file
    output:
        1. gdf : GeoDataFrame of the queried water features'''
    
    # Add paths to different water related geopackage files
    paths = [ os.path.join(BASE_PATH,r"wtr_ntwk_waterpoint\wtr_ntwk_waterpoint.gpkg"),
              os.path.join(BASE_PATH,r"wtr_ntwk_water\wtr_ntwk_water.gpkg")]
    
    # Read the geopackage files into geopandas dataframes
    gdf_list = [gpd.read_file(path) for path in paths]

    # Set the coordinate reference system to EPSG:27700 (British National Grid) nad apply bbox if provided
    if bbox:
        entent_polygon_file = joblib.load(os.path.join(ARTIFACT_PATH,f"{bbox}.pkl"))
        extent_polygon = entent_polygon_file.data.to_crs(epsg=27700)
        gdf_list = [gpd.clip(gdf, extent_polygon) for gdf in gdf_list]
    
    
    # Assign attributes to each GeoDataFrame
    gdf_attrs_list =[{"name":f"waterpoint_{filename}","description":"A geopandas dataframe containing water point data with bbox applied as per user request.","count":len(gdf_list[0])},
                     {"name":f"water_{filename}","description":"A geopandas dataframe containing water data with bbox applied as per user request.","count":len(gdf_list[1])}]
    
    for index, gdf in enumerate(gdf_list):
        gdf.attrs = gdf_attrs_list[index]
    
    if len(gdf_list) == 0:
        return None
    return gdf_list



def query_water_network(bbox:str, filename:str):
    '''Utility function to query OS Data Hub Water Network API
    args:
        1. bbox : NGD Extent to limit the query
        2. filename : name of the output file
    output:
        1. gdf : GeoDataFrame of the queried water network features'''
    
    # Add paths to different water network related geopackage files
    paths = [ os.path.join(BASE_PATH,r"wtr_ntwk_waterlinkset\wtr_ntwk_waterlinkset.gpkg"),
              os.path.join(BASE_PATH,r"wtr_ntwk_waterlink\wtr_ntwk_waterlink.gpkg")]
    
    # Read the geopackage files into geopandas dataframes
    gdf_list = [gpd.read_file(path) for path in paths]

    # Set the coordinate reference system to EPSG:27700 (British National Grid) nad apply bbox if provided
    if bbox:
        entent_polygon_file = joblib.load(os.path.join(ARTIFACT_PATH,f"{bbox}.pkl"))
        extent_polygon = entent_polygon_file.data.to_crs(epsg=27700)
        gdf_list = [gpd.clip(gdf, extent_polygon) for gdf in gdf_list]
      
    
    # Assign attributes to each GeoDataFrame
    gdf_attrs_list =[{"name":f"waterlinkset_{filename}","description":"A geopandas dataframe containing water link set data with bbox applied as per user request.","count":len(gdf_list[0])},
                     {"name":f"waterlink_{filename}","description":"A geopandas dataframe containing water link data with bbox applied as per user request.","count":len(gdf_list[1])}]
    
    for index, gdf in enumerate(gdf_list):
        gdf.attrs = gdf_attrs_list[index]
    
    if len(gdf_list) == 0:
        return None
    return gdf_list


def query_land_features(bbox:str, filters:list, filename:str):
    '''Utility function to query OS Data Hub Land API
    args:
        1. bbox : NGD Extent to limit the query
        2. filter : list of filters to apply to the query
        3. filename : name of the output file
    output:
        1. gdf : GeoDataFrame of the queried land features
    '''
    # Add paths to different land related geopackage files
    paths = [ os.path.join(BASE_PATH,r"lnd_fts_land\lnd_fts_land.gpkg"),
              os.path.join(BASE_PATH,r"lnd_fts_landpoint\lnd_fts_landpoint.gpkg"),
              os.path.join(BASE_PATH,r"lnd_fts_landform\lnd_fts_landform.gpkg"),
              os.path.join(BASE_PATH,r"lnd_fts_landformline\lnd_fts_landformline.gpkg"),
              os.path.join(BASE_PATH,r"lnd_fts_landformpoint\lnd_fts_landformpoint.gpkg")]
    
    # Read the geopackage files into geopandas dataframes
    gdf_list = [gpd.read_file(path) for path in paths]

    # Set the coordinate reference system to EPSG:27700 (British National Grid) nad apply bbox if provided
    if bbox:
        entent_polygon_file = joblib.load(os.path.join(ARTIFACT_PATH,f"{bbox}.pkl"))
        extent_polygon = entent_polygon_file.data.to_crs(epsg=27700)
        gdf_list = [gpd.clip(gdf, extent_polygon) for gdf in gdf_list]
    
    if filters:
        gdf_filtered = []
        for gdf in gdf_list:
            data_filtered = []
            for filter in filters:
                data_filtered.append(gdf[gdf["description"] == filter])
            gdf_filtered.append(pd.concat(data_filtered, ignore_index=True))
        gdf_list = gdf_filtered

    # Assign attributes to each GeoDataFrame
    gdf_attrs_list =[{"name":f"land_{filename}","description":"A geopandas dataframe containing land data with filters and bbox applied as per user request.","count":len(gdf_list[0])},
                     {"name":f"landpoint_{filename}","description":"A geopandas dataframe containing land point data with filters and bbox applied as per user request. Further name filtering is available for this","count":len(gdf_list[1])},
                     {"name":f"landform_{filename}","description":"A geopandas dataframe containing land form data with filters and bbox applied as per user request.","count":len(gdf_list[2])},
                     {"name":f"landformline_{filename}","description":"A geopandas dataframe containing land form line data with filters and bbox applied as per user request. Further name filtering is available for this","count":len(gdf_list[3])},
                     {"name":f"landformpoint_{filename}","description":"A geopandas dataframe containing land form point data with filters and bbox applied as per user request.Further name filtering is available for this","count":len(gdf_list[4])}]
    
    for index, gdf in enumerate(gdf_list):
        gdf.attrs = gdf_attrs_list[index]
    
    # Return None if no dataframes are left after filtering
    gdf_list = [gdf for gdf in gdf_list if not gdf.empty]
    
    if len(gdf_list) == 0:
        return None
    
    return gdf_list