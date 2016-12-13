if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Fetch dependencies
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3 python3-pip pyton3-psyopg2 postgresql postgresql-contrib apache2
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

# Initialize postgres server
sudo systemctl enable postgresql.service

