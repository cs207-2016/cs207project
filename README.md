# CS207 Team 3 Final Project

[![Build Status](https://travis-ci.org/cs207-2016/cs207project.svg?branch=master)](https://travis-ci.org/cs207-2016/cs207project)

[Website URL](http://ec2-174-129-135-178.compute-1.amazonaws.com/)

Team 3:<br>
Yamini Bansal<br>
Ariel Herbert-Voss<br>
Sophie Hilgard<br>
Ryan Lapcevic<br>
Anthony Soroka<br>

<p>This project is organized into two python libraries, a systemd service, and a flask-based website. Each of these occupies its own directory in the src/ directory.</p>

<p>The centerpiece of this project is the Postgres and Flask-backed website, which enables users to upload and query time series based on similarity as determined by a kernel function.</p>

<p>The website depends on our `timeseries` library for manipulating time series and a systemd service running a red-black tree-based database for determining proximity between time series. This database depends on our `rbtree` library for its red-black tree, and communicates with clients over a unix socket.</p>

<p>To install this project on a fresh Amazon EC2 instance running the default Ubuntu 16.04 image, execute the following command from the project's root directory:</p>

```bash

	sudo ./init.sh
```

<p>This will install the project's dependencies, install the systemd service, initialize its Postgres database, and initialize the Apache webserver serving the website.</p>

<p> The project is organized as follows:</p>

src/
	dbserver/: A red-black tree-based database for querying proximity between time series. This is implemented as a pip-installable library, which is used by a simple systemd service to serve queries over a socket.<br>
	timeseries/: A library for storing and manipulating time series.<br>
	rbtree/: An implementation of a red-black tree as a library.<br>
	website/: The project website, implemented using flask. <br>

<p>To build the `dbserver`, `timeseries`, or `rbtree` packages independently, run `make sdist` from the root directory of the project. The pip-installable python packages will be stored in the `dist` directory.</p>

<p>To run our unit tests, run `make test` from the root of the project.</p>

<p>JSON files must be of the following format:</p><br>

```json
{
  'time_points' : [<time points>],
  'data_points' : [<data points>]
}
```

<p>Time series identifiers are managed internally and need not be included in the uploaded file.</p>
