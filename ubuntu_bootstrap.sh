apt-get update && apt-get upgrade -y

add-apt-repository ppa:graphics-drivers/ppa
apt-get install ubuntu-drivers-common
apt-get install nvidia-driver-440
watch -d -n 0.5 nvidia-smi

apt-get install apt-transport-https ca-certificates curl software-properties-common glances
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository  "deb [arch=amd64] https://download.docker.com/linux/ubuntu  $(lsb_release -cs) stable"

curl -L https://github.com/docker/compose/releases/download/1.25.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

apt-get update

wget https://repo.continuum.io/archive/Anaconda3-2019.10-Linux-x86_64.sh
sh Anaconda3-2019.10-Linux-x86_64.sh > /dev/null
source .bashrc
rm Anaconda3-2019.10-Linux-x86_64.sh
conda config --set auto_activate_base false
conda config --append channels conda-forge

conda update conda
conda update anaconda
conda update --all
conda activate

add-apt-repository universe
add-apt-repository ppa:certbot/certbot
apt-get update
apt-get install python-certbot-nginx

cerbot --nginx
certbot renew --dry-run

git clone https://github.com/Distortedlogic/theStonkMarket.git
cd theStonkMarket

pip install gdown
gdown -O flask/Stonks/models/template_clf.h5 --id 13RE5UKe5GeIefLhA7kb46z-iSXulVcp4

docker-compose up --build
