import sys
import re

def process(gpx_data):
    return re.sub(
        r'<trkpt(.*?)>\s*</trkpt>', r'<trkpt\1 />', 
        gpx_data,
    )

def main():
    gpx_data = sys.stdin.read()
    print(
       process(gpx_data) 
    )
    
if __name__ == "__main__":
    main()