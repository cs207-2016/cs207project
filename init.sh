if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3 python3-pip pyton3-psyopg2 postgresql postgresql-contrib apache2
sudo pip3 install flask Flask_SQLAlchemy
sudo useradd -r -s /bin/false dbserver
sudo mkdir /var/dbserver
sudo chown /var/dbserver dbserver:dbserver


