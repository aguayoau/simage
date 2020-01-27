#!/bin/bash
set -o xtrace
sudo yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
sudo yum install -y python3 python3-pip python3-devel git httpd httpd-devel gcc

#sqlite 3.8.7 is requiremnt of Django 2.2.4 and is not in the default repos
wget ftp://ftp.pbone.net/mirror/archive.fedoraproject.org/fedora/linux/releases/21/Cloud/x86_64/os/Packages/s/sqlite-3.8.7-1.fc21.x86_64.rpm 
sudo yum install -y sqlite-3.8.7-1.fc21.x86_64.rpm


cat << _EOF_ > /home/ec2-user/setup.sh
set -o xtrace
python3 -m venv dax112
source dax112/bin/activate
pip install amazon-dax-client==1.1.2 django==2.2.4
deactivate

python3 -m venv dax114
source dax114/bin/activate
pip install amazon-dax-client==1.1.4 django==2.2.4
deactivate

git clone https://github.com/aguayoau/dax_testing.git
_EOF_

cat << _EOF_ > /home/ec2-user/dax-params.sh
export DAX_ENDPOINT=users.hnmf4p.clustercfg.dax.apse2.cache.amazonaws.com:8111
export DAX_REGION_NAME=ap-southeast-2
_EOF_

cat << _EOF_ > /home/ec2-user/test112.sh
set -o xtrace
source dax-params.sh
source dax112/bin/activate
cd ~/dax_testing
export PRIVATEIP=\$(hostnamectl | grep Static | awk '{print \$3}')
python manage.py runserver \$PRIVATEIP:8080
deactivate
cd ~
_EOF_

cat << _EOF_ > /home/ec2-user/test114.sh
set -o xtrace
source dax-params.sh
source dax114/bin/activate
cd ~/dax_testing
export PRIVATEIP=\$(hostnamectl | grep Static | awk '{print \$3}')
python manage.py runserver \$PRIVATEIP:8080
deactivate
cd ~
_EOF_

chown -R ec2-user:ec2-user /home/ec2-user/*
chmod -R 755 /home/ec2-user/*.sh

printf "\n########################\n\n     please execute setup.sh to configure the test\n     then modify the file dax-params.sh and put your values\n     You can use test112.sh to test verion 1.1.2\n     or test114.sh to test verion 1.1.4\n\n     test with the browser on the using port 8080\n\n########################\n" | sudo tee -a /etc/motd

