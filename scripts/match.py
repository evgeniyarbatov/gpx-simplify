import sys
import gpxpy

import requests
import itertools
import polyline

import xml.dom.minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from utils import (
    log,
    get_gpx_df,
)

DEFAULT_RADIUS_IN_METERS = 10

def osrm_format(coords):
    lat, lon = coords
    return f"{lon},{lat}"

def get_match(points):
    radiuses = ';'.join([str(DEFAULT_RADIUS_IN_METERS)] * len(points))
    points = ';'.join(map(osrm_format, points))
    
    params = {
        'geometries': 'polyline6',
        'radiuses': radiuses,
    } 
    response = requests.get(f"http://127.0.0.1:6000/match/v1/foot/{points}", params=params)
    routes = response.json()
    
    if routes['code'] != 'Ok':
        return []
    
    route = [
        polyline.decode(matching['geometry'], 6)
        for matching in routes['matchings']
    ]

    return list(itertools.chain.from_iterable(route))

def create_gpx(route):
    gpx = Element('gpx', {
        'creator': 'Evgeny Arbatov',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation': 'http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd',
        'version': '1.1',
        'xmlns': 'http://www.topografix.com/GPX/1/1'
    })
    trk = SubElement(gpx, "trk")
    trkseg = SubElement(trk, "trkseg")

    for lat, lng in route:
        SubElement(trkseg, "trkpt", attrib={"lat": str(lat), "lon": str(lng)})

    gpx = xml.dom.minidom.parseString(
        tostring(gpx, encoding="unicode")
    ).toprettyxml() 
        
    return gpx

def process(filename, gpx_data):
    original_gpx = gpxpy.parse(gpx_data)

    complete_route = []
    df = get_gpx_df(original_gpx)
    
    for (_, row1), (_, row2) in zip(df.iterrows(), df.iloc[1:].iterrows()):
        matched_route = get_match([
            (row1['latitude'], row1['longitude']),
            (row2['latitude'], row2['longitude']),
        ])
        complete_route.append(matched_route)

    complete_route = list(itertools.chain.from_iterable(complete_route))
    
    edited_gpx = create_gpx(complete_route)       
    edited_gpx = gpxpy.parse(edited_gpx)

    log(filename, original_gpx, edited_gpx, 'osrm-match')
    
    return edited_gpx.to_xml()

def main(args):
    filename = args[0]
    
    gpx_data = sys.stdin.read()
    print(
       process(filename, gpx_data) 
    )
    
if __name__ == "__main__":
    main(sys.argv[1:])