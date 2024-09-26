# gpx-simplify

Given 100km GPX file simplify it to reduce number of points while keeping directions accurate:

- Douglas–Peucker algorithm on raw GPX
- OSRM matching service to match each pair of coordinates to the closest point on OSM map
- Douglas–Peucker algorithm one more time
- Query OSRM nearest service to resolve OSM node IDs for each point
- Query Overpass API to count ways through each pair of node IDs
- Iterate on Overpass API query by increasing distance between node IDs
- Stop querying Overpass API when there is more than 1 way between a pair of node IDs

The result is a GPX file with points which contain only a single OSM ID through them.

## Run

Add original GPX to `original-gpx` dir.

Run `make` to simplify.

Simplified GPX in `simplified-gpx` dir.