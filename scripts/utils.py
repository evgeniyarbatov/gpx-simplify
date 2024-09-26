import logging
import os
import gpxpy

import pandas as pd

from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

from geopy.distance import geodesic

LOG_DIR = 'log'
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=f"{LOG_DIR}/simplify.log", 
    filemode='a',
    encoding='utf-8', 
    level=logging.INFO,
    format='%(message)s',
)
 
def parse_gpx(filepath):
	data = []  

	with open(filepath, 'r') as gpx_file:
		gpx = gpxpy.parse(gpx_file)
    
	for track in gpx.tracks:
		for segment in track.segments:
			for point in segment.points:
				lat, lng = point.latitude, point.longitude
				data.append({
					'latitude': lat, 
					'longitude': lng,
				})

	return pd.DataFrame(data)

def get_gpx_coordinates(gpx):
    coordinates = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coordinates.append((
                    point.latitude, 
                    point.longitude,
                ))
    return coordinates

def get_dtw_distance(original_gpx, edited_gpx):
	original_coordinates = get_gpx_coordinates(original_gpx)
	edited_coordinates = get_gpx_coordinates(edited_gpx)
 
	distance, _ = fastdtw(
		original_coordinates, 
		edited_coordinates, 
		dist=euclidean,
  	)
 
	return distance

def get_stats(gpx):
    count, distance = 0, 0.0
    for track in gpx.tracks:
        for segment in track.segments:
            count += len(segment.points)
            for i in range(1, len(segment.points)):
                point1 = segment.points[i - 1]
                point2 = segment.points[i]
                
                distance += geodesic(
                    (point1.latitude, point1.longitude), 
                    (point2.latitude, point2.longitude),
                ).kilometers

    return count, round(distance, 2) 

def log(
    filename,
    original_gpx, 
    edited_gpx, 
    step,
):
    logger = logging.getLogger(__name__)
    
    original_count, original_distance = get_stats(original_gpx)
    new_count, new_distance = get_stats(edited_gpx)
    dtw_distance = get_dtw_distance(original_gpx, edited_gpx)
    
    logger.info(
        '%s,%d,%f,%d,%f,%f,%s',
        os.path.basename(filename),
        original_count, 
        original_distance,
        new_count, 
        new_distance, 
        dtw_distance,
        step,
    )