#!/bin/bash
set -e

# Install Docker
apt-get install apt-transport-https ca-certificates curl gnupg2 software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
apt-get update
apt-get install docker-ce

# Prepare config
echo -n "Enter telegram API token and press [ENTER]: "
read token
echo -n "Enter transmission URL and press [ENTER]: "
read transmission_host
echo -n "Enter transmission port and press [ENTER]: "
read transmission_port
echo -n "Enter username to access ${transmission_host} and press [ENTER]: "
read transmission_user
echo -n "Enter password for ${transmission_user} and press [ENTER]: "
read transmission_password
echo -n "Enter transmission download dir and press [ENTER]: "
read transmission_download_dir
cat > ./app/config << EOL
[telegram]
token = ${token}

[transmission]
transmission_host = ${transmission_host}
transmission_port = ${transmission_port}
transmission_user = ${transmission_user}
transmission_password = ${transmission_password}
transmission_download_dir = ${transmission_download_dir}
EOL

# Build image
docker build -t transmission_mgmt_bot_image .

# Run container from image
docker run -d --name=transmission_mgmt_bot -v ~/transmission_mgmt_bot_app:/mnt transmission_mgmt_bot_image
