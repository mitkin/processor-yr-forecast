# processor-yr-forecast
Retrieve location forecast using api.met.no

## Dependencies
xmltodict

## Elevation data
Note that api.met.no does not automatically find the surface elevation outside Norway.
To overcome this and stay lightweight the elevation data is pulled from mapbox elevation api.
It requires registration, but at the time of the commit 50K request per month are allowed for free.
