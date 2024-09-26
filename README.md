# gpx-simplify

Given GPX file of 100km ultra simplify it to reduce number of points while keeping directions accurate.

Idea:

- Douglas–Peucker algorithm on raw GPX with 5m limit (5m being average GPS accuracy)
- OSRM matching service to match each pair of coordinates to the closest point on OSM map
- Douglas–Peucker algorithm one more time (OSRM will return a lot of points)
- Query OSRM nearest service to resolve OSM node IDs for each point
- Query Overpass API to count amount of ways through each pair of node IDs
- Iterate on Overpass API query by increasing distance between node IDs until we have more than 1 way through pair of node IDs

The result is a GPX file with points which contain only a single OSM ID through them.
