# CS207 Team 3 Website Library

Creates a Flask website with SQLAlchemy database to store the postgresql metadata for each Timeseries (ID, blarg, level, mean, std, fpath)

From metadata range parameters can retrieve all of the Timeseries IDs in the database matching those parameters.

Returns a list of the 5 most similar IDs in response to a query of either an uploaded Timeseries or a Timeseries ID.

Unless otherwise specified, runs on port 8080.
