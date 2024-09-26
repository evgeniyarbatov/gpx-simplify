import sys
import gpxpy
import requests

import pandas as pd

from utils import (
    log,
    get_gpx_df,
    create_gpx,
)

def get_nearest(coords):
  lat, lon = coords
  response = requests.get(f"http://127.0.0.1:6000/nearest/v1/foot/{lon},{lat}")
  response.raise_for_status()

  df = None
  
  data = response.json()
  if 'waypoints' in data:
      waypoints = data['waypoints']
      info = [(
        lat,
        lon,
        wp['nodes'],
      ) for wp in waypoints]
      df = pd.DataFrame(info, columns=[
        'lat',
        'lon',
        'nodes',
      ])
  
  return df

def query_osrm_nearest(df):
  results = []
  
  for _, row in df.iterrows():
    nearest_df = get_nearest((row['latitude'], row['longitude']))
    results.append(nearest_df)

  return pd.concat(results).reset_index(drop=True)

def query_overpass_api(nodes, lat, lon):
    node_1, node_2 = nodes
    overpass_query = f"""
        [out:json];
        node(id:{node_1}, {node_2});
        way(bn);
        out count;
    """

    response = requests.get(
        "http://localhost:8000/api/interpreter", 
        params={'data': overpass_query}
    )
    data = response.json()

    way_count = data['elements'][0]['tags']['ways']

    info = [(
        lat,
        lon,
        nodes,
        way_count,
    )]

    df = pd.DataFrame(info, columns=[
        'lat',
        'lon',
        'nodes',
        'way_count',
    ])

    return df

def filter_with_ways(df):
  results = []
  
  idx, inner_idx = None, None
  
  for idx, row in df.iterrows():
    if inner_idx != None:
        if idx < inner_idx:
            continue
      
    overpass_df = query_overpass_api(row['nodes'], row['lat'], row['lon'])
    if overpass_df.loc[0, 'way_count'] == 1:
        for inner_idx in range(idx, len(df)):
            inner_row = df.loc[inner_idx]
            result_df = query_overpass_api(
                [
                    row['nodes'][0],
                    inner_row['nodes'][0],
                ], 
                inner_row['lat'], 
                inner_row['lon'],
            )
            if result_df.loc[0, 'way_count'] > 1:
                info = [
                    (
                        row['lat'], 
                        row['lon'],
                        row['nodes'],
                        overpass_df.loc[0, 'way_count'],
                    ),
                    (
                        result_df.loc[0, 'lat'], 
                        result_df.loc[0, 'lon'], 
                        result_df.loc[0, 'nodes'], 
                        result_df.loc[0, 'way_count'],
                    ),
                ]
                
                overpass_df = pd.DataFrame(info, columns=[
                    'lat',
                    'lon',
                    'nodes',
                    'way_count',
                ])             
        
                results.append(overpass_df)
    else:
        results.append(overpass_df)
        
  return pd.concat(results).reset_index(drop=True)

def process(filename, gpx_data):
    original_gpx = gpxpy.parse(gpx_data)
    edited_gpx = gpxpy.parse(gpx_data)
    
    df = get_gpx_df(original_gpx)
    osrm_df = query_osrm_nearest(df)
    ways_df = filter_with_ways(osrm_df)
    
    route = list(zip(ways_df['lat'], ways_df['lon']))
    edited_gpx = create_gpx(route)       
    edited_gpx = gpxpy.parse(edited_gpx)
    
    log(filename, original_gpx, edited_gpx, 'overpass-api')
    
    return edited_gpx.to_xml()

def main(args):
    filename = args[0]
    
    gpx_data = sys.stdin.read()
    print(
       process(filename, gpx_data) 
    )
    
if __name__ == "__main__":
    main(sys.argv[1:])