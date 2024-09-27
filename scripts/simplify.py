import sys
import gpxpy

from utils import log

def process(gpx_data):
    original_gpx = gpxpy.parse(gpx_data)
    edited_gpx = gpxpy.parse(gpx_data)
    
    edited_gpx.simplify(max_distance=5.0)
    log(original_gpx, edited_gpx, 'douglas–peucker')
    
    return edited_gpx.to_xml()

def main():   
    gpx_data = sys.stdin.read()
    print(
       process(gpx_data) 
    )
    
if __name__ == "__main__":
    main()