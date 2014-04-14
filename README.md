#U.S. Forest Service Active Wildfire Data to GeoJSON

##Background
The U.S. forest service publishes a KMZ file with information on active wildfires happening in the United States. This KMZ file contains polygons and placemarks that denote detection footprints and centroids for each active wildfire. The KMZ format is great for visualizing the data in Google Earth, but not particularly handy for loading this fire data into a relational database.

##U.S. Forest Service Active Fire Mapping Program website
http://activefiremaps.fs.fed.us/

##Workflow
1. Grab the conus.kmz file from the U.S. Forest Service website
2. Unzip the KMZ in memory and read the KML file contained inside
3. Parse out the centroids for wildfires over the last 12 hours
4. Create a GeoJSON object
