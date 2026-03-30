import geopandas as gpd
import os
import pandas as pd
import joblib
import warnings
from pathlib import Path
import ast

warnings.filterwarnings("ignore")

BASE_PATH = Path.cwd() / "osm_data" #r"C:/Users/ab1574/OneDrive - University of Exeter/Desktop/Ordnance_Survey/os_ngd_sample"
ARTIFACT_PATH = Path.cwd() / "artifacts"


def get_filterable_features(collection:str,description:str):

    '''Get filterable categories for collections. For OSM it is the same column as the dataset
    Args:
    collection : str, the collection name
    description: str, the column name which contains the filterable categories for the collection.
    returns:
    dict : The filterable categories for the collection'''

    gdf = gpd.read_file(os.path.join(BASE_PATH, f"{collection}.gpkg"))
    return gdf[description].unique().tolist()
    

def query_address(filters:list, bbox:str, street_address:bool, filename:str, query:str):
    '''Utility function to query OS Data Hub Address API
    args:
        1. filters : list of filters to apply to the query
        2. bbox : NGD Extent to limit the query
        3. street_address : boolean to indicate if street address is required
    output:
        1. gdf : GeoDataFrame of the queried addresses'''
    
    paths = [os.path.join(BASE_PATH,r"devon_pois.gpkg")]
    
    gdf_list = [gpd.read_file(path) for path in paths]
    gdf = pd.concat(gdf_list, ignore_index=True)
    gdf = gdf.set_crs(epsg=27700)

    if bbox and bbox != 'None':
        entent_polygon_file = joblib.load(os.path.join(ARTIFACT_PATH,f"{bbox}.pkl"))
        extent_polygon = entent_polygon_file.data.to_crs(epsg=27700)
        gdf = gpd.clip(gdf, extent_polygon)
    
    
    if not street_address:
        gdf.attrs = {"name":f"{filename}","description":f"A geopandas dataframe containing address data with bbox applied but no filters applied for the query {query}. (so remember no search is performed here so spurious entities present)","count":len(gdf)}
    else:
        gdf.attrs = {"name":f"{filename}","description":f"A geopandas dataframe containing address data with bbox applied but no filters applied for the query {query}. (so remember no search is performed here so spurious entities present)","count":len(gdf)}

    if gdf.empty:
        return None

    return gdf

def query_buildings(filters:list, bbox:str, filename:str, query:str):
    '''Utility function to query OS Data Hub Building API
    args:
        1. filters : list of filters to apply to the query
        2. bbox : NGD Extent to limit the query
    output:
        1. gdf : GeoDataFrame of the queried buildings'''
    
    # Add paths to different building related geopackage files
    paths = [ os.path.join(BASE_PATH,r"devon_buildings.gpkg")]
    
    # Read the geopackage files into geopandas dataframes
    gdf_list = [gpd.read_file(path) for path in paths]

    # Set the coordinate reference system to EPSG:27700 (British National Grid) nad apply bbox if provided
    if bbox and bbox != 'None':
        entent_polygon_file = joblib.load(os.path.join(ARTIFACT_PATH,f"{bbox}.pkl"))
        extent_polygon = entent_polygon_file.data.to_crs(epsg=27700)
        gdf_list = [gpd.clip(gdf, extent_polygon) for gdf in gdf_list]
    
    # Apply filters to each of the dataframes and concatenate the results of multiple filters
    gdf_filtered = []
    if filters is not None and filters !="None" and not isinstance(filters,list):
        try:
            filters = ast.literal_eval(filters)
        except Exception as e:
            raise TypeError("Filters need to be a list")
        
    if isinstance(filters,list) and len(filters) > 0:
        for gdf in gdf_list:
            gdf_temp = []
            for filter in filters:
                gdf_temp.append(gdf[gdf["building"] == filter])
            gdf_filtered.append(pd.concat(gdf_temp, ignore_index=True))
    else:
        gdf_filtered = gdf_list

    
    # Assign attributes to each GeoDataFrame
    gdf_attrs_list =[{"name":f"buildings_{filename}","description":f"A geopandas dataframe containing building data with filters and bbox applied for the query {query} using filters {filters}.","count":len(gdf_filtered[0])}]
    
    gdf_list = [gdf for gdf in gdf_filtered if not gdf.empty]
    gdf_attrs_list = [gdf_attrs_list[i] for i in range(len(gdf_filtered)) if not gdf_filtered[i].empty]
    # Return None if no dataframes are left after filtering
    for index, gdf in enumerate(gdf_list):
        gdf.attrs = gdf_attrs_list[index]
    
    if len(gdf_list) == 0:
        return None
    
    return gdf_list

def apply_extent_named_area(bbox:str, polygon_or_point:bool,filename:str,query:str):
    '''Utility function to apply bbox to named area data
    args:
        1. bbox : NGD Extent to limit the query
        2. polygon_or_point : boolean to indicate if bbox is a polygon or point
    output:
        1. gdf : GeoDataFrame of the queried named areas'''
    
    # Determine the path to the named area geopackage file based on whether polygon or point data is requested
    if polygon_or_point == True or polygon_or_point == "True":
        path = os.path.join(BASE_PATH,r"devon_boundaries.gpkg")
    

    # Read the geopackage file into a geopandas dataframe and set the coordinate reference system to EPSG:27700 (British National Grid) and apply bbox if provided
    gdf = gpd.read_file(path)
    gdf = gdf.set_crs(epsg=27700)
    print("bbox is ",bbox, type(bbox), polygon_or_point, type(polygon_or_point))

    if bbox and bbox != 'None':
        entent_polygon_file = joblib.load(os.path.join(ARTIFACT_PATH,f"{bbox}.pkl"))
        extent_polygon = entent_polygon_file.data.to_crs(epsg=27700)
        gdf = gpd.clip(gdf, extent_polygon)
    
    gdf.attrs = {"name":f"{filename}","description":f"A geopandas dataframe containing named area data with no filters applied for the query (so remember no search is performed here so spurious entities present) {query}.","count":len(gdf)}
    return gdf



def query_water_network(bbox:str, filename:str,query:str):
    '''Utility function to query OS Data Hub Water Network API
    args:
        1. bbox : NGD Extent to limit the query
        2. filename : name of the output file
    output:
        1. gdf : GeoDataFrame of the queried water network features'''
    
    # Add paths to different water network related geopackage files
    paths = [ os.path.join(BASE_PATH,r"devon_waterways.gpkg")]
    
    # Read the geopackage files into geopandas dataframes
    gdf_list = [gpd.read_file(path) for path in paths]

    # Set the coordinate reference system to EPSG:27700 (British National Grid) nad apply bbox if provided
    if bbox and bbox != 'None':
        entent_polygon_file = joblib.load(os.path.join(ARTIFACT_PATH,f"{bbox}.pkl"))
        extent_polygon = entent_polygon_file.data.to_crs(epsg=27700)
        gdf_list = [gpd.clip(gdf, extent_polygon) for gdf in gdf_list]
      
    if filters is not None and filters !="None" and not isinstance(filters,list):
        try:
            filters = ast.literal_eval(filters)
        except Exception as e:
            raise TypeError("Filters need to be a list")
    
    if filters and len(filters) > 0:
        gdf_filtered = []
        for gdf in gdf_list:
            data_filtered = []
            for filter in filters:
                data_filtered.append(gdf[gdf["waterway"] == filter])
            gdf_filtered.append(pd.concat(data_filtered, ignore_index=True))
        gdf_list = gdf_filtered
    
    # Assign attributes to each GeoDataFrame
    gdf_attrs_list =[{"name":f"waterway_{filename}","description":f"A geopandas dataframe containing water link set data with bbox applied for the query {query} with filters applied  {filters} for the query ","count":len(gdf_list[0])}]
    
    gdf_attrs_list = [gdf_attrs_list[i] for i in range(len(gdf_list)) if not gdf_list[i].empty]
    gdf_list = [gdf for gdf in gdf_list if not gdf.empty]

    for index, gdf in enumerate(gdf_list):
        gdf.attrs = gdf_attrs_list[index]
    
    if len(gdf_list) == 0:
        return None
    return gdf_list


def query_land_features(bbox:str, filters:list, filename:str,query:str):
    '''Utility function to query OS Data Hub Land API
    args:
        1. bbox : NGD Extent to limit the query
        2. filter : list of filters to apply to the query
        3. filename : name of the output file
    output:
        1. gdf : GeoDataFrame of the queried land features
    '''
    # Add paths to different land related geopackage files
    paths = [ os.path.join(BASE_PATH,r"devon_natural.gpkg")]
    
    # Read the geopackage files into geopandas dataframes
    gdf_list = [gpd.read_file(path) for path in paths]

    # Set the coordinate reference system to EPSG:27700 (British National Grid) nad apply bbox if provided
    if bbox and bbox != 'None':
        entent_polygon_file = joblib.load(os.path.join(ARTIFACT_PATH,f"{bbox}.pkl"))
        extent_polygon = entent_polygon_file.data.to_crs(epsg=27700)
        gdf_list = [gpd.clip(gdf, extent_polygon) for gdf in gdf_list]
    
    if filters is not None and filters !="None" and not isinstance(filters,list):
        try:
            filters = ast.literal_eval(filters)
        except Exception as e:
            raise TypeError("Filters need to be a list")
    
    if filters and len(filters) > 0:
        gdf_filtered = []
        for gdf in gdf_list:
            data_filtered = []
            for filter in filters:
                data_filtered.append(gdf[gdf["natural"] == filter])
            gdf_filtered.append(pd.concat(data_filtered, ignore_index=True))
        gdf_list = gdf_filtered
    

    # Assign attributes to each GeoDataFrame
    gdf_attrs_list =[{"name":f"land_{filename}","description":f"A geopandas dataframe containing land data with filters and bbox applied for the query {query} using filters {filters}. ","count":len(gdf_list[0])}]
    
    for index, gdf in enumerate(gdf_list):
        gdf.attrs = gdf_attrs_list[index]
    
    # Return None if no dataframes are left after filtering
    gdf_list = [gdf for gdf in gdf_list if not gdf.empty]
    
    if len(gdf_list) == 0:
        return None
    
    return gdf_list


def query_land_use(bbox:str,filters:list,filename:str,query:str):
    '''Utility function to query OS Data Hub Land API
    args:
        1. bbox : NGD Extent to limit the query
        2. filter : list of filters to apply to the query
        3. filename : name of the output file
    output:
        1. gdf : GeoDataFrame of the queried land features
    '''
    paths = [ os.path.join(BASE_PATH,r"devon_landuse.gpkg")]
    
    # Read the geopackage files into geopandas dataframes
    gdf_list = [gpd.read_file(path) for path in paths]

    # Set the coordinate reference system to EPSG:27700 (British National Grid) nad apply bbox if provided
    if bbox and bbox != 'None':
        entent_polygon_file = joblib.load(os.path.join(ARTIFACT_PATH,f"{bbox}.pkl"))
        extent_polygon = entent_polygon_file.data.to_crs(epsg=27700)
        gdf_list = [gpd.clip(gdf, extent_polygon) for gdf in gdf_list]
    
    if filters is not None and filters !="None" and not isinstance(filters,list):
        try:
            filters = ast.literal_eval(filters)
        except Exception as e:
            raise TypeError("Filters need to be a list")
        
    if filters and len(filters) > 0:
        gdf_filtered = []
        for gdf in gdf_list:
            data_filtered = []
            for filter in filters:
                data_filtered.append(gdf[gdf["landuse"] == filter])
            gdf_filtered.append(pd.concat(data_filtered, ignore_index=True))
        gdf_list = gdf_filtered

    # Assign attributes to each GeoDataFrame
    gdf_attrs_list =[{"name":f"landuse_{filename}","description":f"A geopandas dataframe containing land use data with filters and bbox applied for the query {query} using filters {filters}. Further Name filtering is available for this","count":len(gdf_list[0])}]
    
    for index, gdf in enumerate(gdf_list):
        gdf.attrs = gdf_attrs_list[index]
    
    # Return None if no dataframes are left after filtering
    gdf_list = [gdf for gdf in gdf_list if not gdf.empty]
    
    if len(gdf_list) == 0:
        return None
    
    return gdf_list

