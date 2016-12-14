# CS207 Team 3 Time Series Library

[![Build Status](https://travis-ci.org/cs207-2016/cs207project.svg?branch=master)](https://travis-ci.org/cs207-2016/cs207project)

A library for working with time series.

A time series is an ordered series of data point indexed by or associated with time points. See [Wikipedia](https://en.wikipedia.org/wiki/Time_series) for more information.

The time series library is organized into a tree hierarchy. All time series are iterable. Classes that implement SizedContainerTimeSeriesInterface store data in an underlying data structure. Classes implementing StreamTimeSeriesInterface deal with data in on-line fashion without storing specific time and data points.   

StorageManagerInterface is a an interface for managing persistent storage of time series under an identifier.

SMTimeSeries implements the SizedContainerTimeSeriesInterface using a StorageManager for storage. If no `ident` is supplied, identical time series will receive the same identifier.

## Examples

```python
	from timeseries import *

	time_pts = range(10)
	data_pts = [np.random.rand()*100 for _ in range(10)]
	data_pts2 = [np.random.rand()*100 for _ in range(10)]

	ts1 = TimeSeries(time_pts, data_pts)
	ts2 = TimeSeries(time_pts, data_pts2)

	print(ts1)
	>>> TimeSeries([[0,74.03971533376968]
	[1,69.27105329040427]
	[2,63.36025855256142]
	[3,53.070523275242245]
	[4,70.59362537769765]
	[5,78.88651189882768]
	[6,65.46168446500144]
	[7,46.24432894725656]
	[8,51.65852295580598]
	[9,3.9261801482532777]
	])

	print(ts2)
	>>> TimeSeries([[0,84.16435735195265]
	[1,19.983198578925276]
	[2,16.0760569800653]
	[3,1.1863405900078505]
	[4,24.111065813357826]
	[5,48.70052636724066]
	[6,80.29642724248426]
	[7,77.73321562016949]
	[8,97.52297341149668]
	[9,78.92980490255177]
	])

	# Add, subtract, and multiplication between time series and real numbers supported
	print(ts1 + ts2)
	>>> TimeSeries([[0,158.20407268572234]
	[1,89.25425186932955]
	[2,79.43631553262672]
	[3,54.2568638652501]
	[4,94.70469119105547]
	[5,127.58703826606833]
	[6,145.75811170748568]
	[7,123.97754456742605]
	[8,149.18149636730266]
	[9,82.85598505080505]
	])

	print(ts1 * 2)
	>>> TimeSeries([[0,148.07943066753936]
	[1,138.54210658080854]
	[2,126.72051710512284]
	[3,106.14104655048449]
	[4,141.1872507553953]
	[5,157.77302379765536]
	[6,130.92336893000288]
	[7,92.48865789451312]
	[8,103.31704591161196]
	[9,7.852360296506555]
	])

	# Mean and standard deviation
	print(ts1.mean())
	>>> 57.6512404245

	print(ts1.std())
	>>> 21.574252996592932

	# Iteration through time points
	print([t for t in ts1.itertimes()])
	>>> [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

	# Iteration through data points
	print([t for t in ts1])
	>>> [74.03971533376968, 69.27105329040427, 63.36025855256142, 53.070523275242245, 70.59362537769765, 78.88651189882768, 65.46168446500144, 46.24432894725656, 51.65852295580598, 3.9261801482532777]

	# Iteration through time, value tuples
	print([t for t in ts1.iteritems()])
	>>> [(0, 74.03971533376968), (1, 69.27105329040427), (2, 63.36025855256142), (3, 53.070523275242245), (4, 70.59362537769765), (5, 78.88651189882768), (6, 65.46168446500144), (7, 46.24432894725656), (8, 51.65852295580598), (9, 3.9261801482532777)]

	# All functions implemented one-shot for streaming time series classes
	sts = SimulatedTimeSeries(iter(range(10))
	print([pt for pt in sts.iteritems()])
	>>> [(1478057746, 0), (1478057746, 1), (1478057746, 2), (1478057746, 3), (1478057746, 4), (1478057746, 5), (1478057746, 6), (1478057746, 7), (1478057746, 8), (1478057746, 9)]

```
