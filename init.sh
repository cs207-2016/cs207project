if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Fetch dependencies
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3 python3-pip postgresql postgresql-contrib apache2 libapache2-mod-wsgi-py3 make libpq-dev python-psycopg2
sudo pip3 install flask Flask_SQLAlchemy setuptools pytest SQLAlchemy psycopg2

# Build and install our libraries
make sdist
sudo pip3 install ./dist/timeseries*.tar.gz ./dist/rbtree*.tar.gz ./dist/dbserver*.tar.gz --upgrade --force-reinstall

# Initialize time series database server
sudo useradd -r -s /bin/false dbserver
sudo mkdir /var/dbserver
sudo cp src/dbserver/dbserver.service /etc/systemd/system
sudo cp src/dbserver/start_dbserver.py /var/dbserver
sudo python3 make_ts.py
sudo chmod 777 -R /var/dbserver
sudo chown -R dbserver:dbserver /var/dbserver

# Initialize postgres server
sudo -u postgres bash -c "psql -c \"CREATE USER cs207site WITH PASSWORD 'cs207isthebest';\""
sudo -u postgres bash -c "createdb -w -O cs207site timeseries"
sudo -u postgres bash -c "psql -d timeseries -c \"drop table timeseries;\""
sudo python3 ./populate_postgres.py

# Initialize apache server
sudo rm -rf /var/www/cs207site
sudo cp src/website/cs207site.conf /etc/apache2/sites-available
sudo cp -r src/website /var/www/cs207site
sudo chown ubuntu:ubuntu -R /var/www/cs207site

sudo systemctl daemon-reload
sudo systemctl enable dbserver.service
sudo systemctl start dbserver.service
sudo systemctl enable postgresql.service
sudo systemctl start postgresql.service
sudo a2dissite 000-default.conf
sudo a2ensite cs207site.conf
sudo a2enmod wsgi
sudo service apache2 reload

