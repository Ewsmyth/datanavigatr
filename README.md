# DataNaviGatr
 Ingest, analyze and export data.

## Update Ubuntu Server
```
sudo apt update && sudo apt upgrade -y
```

## Enable Root user password and SSH
#### Set a password for the root user:
```
sudo passwd root
```
#### Enable SSh for the root user:
```
sudo nano /etc/ssh/sshd_config
```
##### Find the line that says:
```
PermitRootLogin prohibit-password
```
##### Change it to:
```
PermitRootLogin yes
```
#### Restart the SSH service:
```
sudo systemctl restart ssh
```

## Install Docker on Ubuntu Server

##### Add Docker's official GPG key:
```
sudo apt-get install ca-certificates curl gnupg
```
```
sudo install -m 0755 -d /etc/apt/keyrings
```
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```
```
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```
##### Add the repository to Apt sources:
```
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
```
sudo apt-get update
```
##### Install Docker packages:
```
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```

## Install Portainer with Docker
##### Create a volume that Portainer Server will use to store its database:
```
sudo docker volume create portainer_data
```
##### Download and install Portainer Server:
```
sudo docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
```
##### Login to the admin account:
```
https://<serverip>:9443
```

## To download and install this application on Docker on Ubuntu Server run the following commands:

##### You can run this command in any directory you want I just run it from the home directory
```
sudo git clone https://github.com/Ewsmyth/datanavigatr.git
```
##### This should be altered to the proper path to the directory you cloned the git into
```
cd datanavigatr
```
##### The period is for if you are inside the "datanavigatr" directory if you are not then you should replace this with the path to the cloned reporter directory
```
sudo docker build -t datanavigatr-image .
```
##### Setup a volume for the the database for persistent storage
```
sudo docker volume create <volume name>
```
###### Example
```
sudo docker volume create datanavigatr-data
```
```
sudo docker volume create qdb1-data
```
```
sudo docker volume create sql-queries
```
```
sudo docker volume create downloaded-data
```
##### Install DataNaviGatr
```
sudo docker run -d -p <port>:<port> --restart=unless-stopped \
    -e SQLALCHEMY_DATABASE_URI='sqlite:///<path of .db file> \
    -e SECRET_KEY='<create a key>' \
    -e HOST='0.0.0.0'
    -e PORT=<port>
    -v <volume name>:/var/lib/docker/volumes/<volume name> \
    reporter-image
```
###### Example
```
sudo docker run -d -p 80:80 --restart=unless-stopped \
    -e HOST='0.0.0.0' \
    -e PORT=80 \
    -e SECRET_KEY='aabbccddeeffgg' \
    -e SQLALCHEMY_DATABASE_URI='sqlite:////var/lib/docker/volumes/datanavigatr-data/datanavigatr-data.db' \
    -e SQLALCHEMY_BINDS_QDB1='sqlite:////var/lib/docker/volumes/qdb1-data/qdb1-data.db' \
    -e SQL_QUERY_DIR='/var/lib/docker/volumes/sql-queries/' \
    -e DOWNLOADED_DB_PATH='/var/lib/docker/volumes/downloaded-data/' \
    -v datanavigatr-data:/var/lib/docker/volumes/datanavigatr-data \
    -v qdb1-data:/var/lib/docker/volumes/qdb1-data \
    -v sql-queries:/var/lib/docker/volumes/sql-queries \
    -v downloaded-data:/var/lib/docker/volumes/downloaded-data \
datanavigatr-image
```