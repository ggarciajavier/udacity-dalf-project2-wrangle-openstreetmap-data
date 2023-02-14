## Udacity Data Analyst Nanodegree Project 2: Wrangle OpenStreetMap data ##

This repository contains the analysis performed by Javier Gómez García for the 2nd project of the Udacity Data Analyst Nanodegree.
It include the following files:

 - A Jupyter notebook containing the main program and the description of the work (Python version: 3.6):
		[Project2_Wrangle_OpenStreetMap_data](Project2_Wrangle_OpenStreetMap_data.ipynb)

 - A sample of the OpenStreetMap of the city I chose for the exercise, A Coruña:
		[LCG_map.osm](LCG_map.osm)

 - The following text files:
		- [MAP_DESCRIPTION](MAP_DESCRIPTION.md): text file containing the link to the map position and the motivation for the choice.
		- [REFERENCES](REFERENCES.md): text file containing the links to the websites and repositories I have used for my work.

 - The following Python files, required to process the data and called by the main program (the .ipynb file), all written in Python 3.6:
		- [audit_street_types](audit_street_types.py): code used to audit the street types and street names
		- [audit_tag_types](audit_tag_types.py): code used to audit the types of tags present in the data
		- [csv2sqldb](csv2sqldb.py): code used to generate a SQL database from a set of CSV files
		- [osm_downsampler](osm_downsampler.py): code used to generate a smaller sample from the full-sized map
		- [osm2csv](osm2csv.py): code used to convert the OSM file (given in XML format) into the CSV files, and to apply the corrections mentioned in the text
		- [schema](schema.py): code providing a dictionary with the required schema to produce the CSV files