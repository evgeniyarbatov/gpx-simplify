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

def get_way_count(nodes):
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

    way_count = int(data['elements'][0]['tags']['ways'])

    return way_count

def get_route(df):
    route = []
    last_idx = -1

    for idx, row in df.iterrows():
        if idx == 0:
            route.append((row['lat'], row['lon']))
            continue
        elif idx == len(df) - 1:
            route.append((row['lat'], row['lon']))
            continue
        
        if idx <= last_idx:
            continue
        
        # Query API for the current row
        way_count = get_way_count(row['nodes'])
        if way_count > 1:
            route.append((row['lat'], row['lon']))
            continue

        # Check subsequent rows
        for inner_idx in range(idx + 1, len(df)):
            inner_row = df.loc[inner_idx]
            
            # Query API with start node from current row and end node from inner row
            way_count = get_way_count([row['nodes'][0], inner_row['nodes'][1]])
            
            if way_count > 1:
                route.append((row['lat'], row['lon']))
                route.append((inner_row['lat'], inner_row['lon']))
                
                last_idx = inner_idx  # Skip to next iteration after finding a match
                break  # Move to next main iteration after finding a match

    return route

def process(filename, gpx_data):
    original_gpx = gpxpy.parse(gpx_data)
    edited_gpx = gpxpy.parse(gpx_data)
    
    df = get_gpx_df(original_gpx)
    osrm_df = query_osrm_nearest(df)
    route = get_route(osrm_df)
    
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