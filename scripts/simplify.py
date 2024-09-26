import sys
import gpxpy

from utils import log

def process(filename, gpx_data):
    original_gpx = gpxpy.parse(gpx_data)
    edited_gpx = gpxpy.parse(gpx_data)
    
    edited_gpx.simplify(max_distance=5.0)
    log(filename, original_gpx, edited_gpx, 'initial-douglas–peucker')
    
    return edited_gpx.to_xml()

def main(args):
    filename = args[0]
    
    gpx_data = sys.stdin.read()
    print(
       process(filename, gpx_data) 
    )
    
if __name__ == "__main__":
    main(sys.argv[1:])