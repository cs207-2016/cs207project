if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Fetch dependencies
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3 python3-pip pyton3-psyopg2 postgresql postgresql-contrib apache2 libapache2-mod-wsgi
sudo pip3 install flask Flask_SQLAlchemy

# Install our libraries
make sdist
sudo pip install ./dist/timeseries*.tar.gz ./dist/rbtree*.tar.gz ./dist/dbserver*.tar.gz

# Initialize time series database server
sudo useradd -r -s /bin/false dbserver
sudo mkdir /var/dbserver
sudo chown dbserver:dbserver /var/dbserver
sudo cp src/dbserver/dbserver.service /etc/systemd/system
sudo cp src/dbserver/start_dbserver.py /var/dbserver
sudo systemctl daemon-reload
sudo systemctl enable dbserver.service
sudo systemctl start dbserver.service

# Initialize postgres server
sudo -u postgres bash -c "psql -c \"CREATE USER cs207site WITH PASSWORD 'cs207isthebest';\""
sudo -u postgres bash -c "createdb -w -O cs207site timeseries"
sudo systemctl enable postgresql.service
sudo systemctl start postgresql.service

# Initialize apache server
sudo a2enmod wsgi
sudo cp src/website/cs207site.conf /etc/apache2/sites-available
sudo cp -r src/website /var/www/cs207site
sudo a2ensite cs207site.conf
