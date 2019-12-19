apt-get update && apt-get upgrade -y

add-apt-repository ppa:graphics-drivers/ppa
apt-get install ubuntu-drivers-common
apt-get install nvidia-driver-440

apt-get install apt-transport-https ca-certificates curl software-properties-common glances
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository  "deb [arch=amd64] https://download.docker.com/linux/ubuntu  $(lsb_release -cs) stable"

curl -L https://github.com/docker/compose/releases/download/1.17.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
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

mkdir theStonkMarket
cd theStonkMarket
git clone https://github.com/Distortedlogic/theStonkMarket.git

sh scripts/dl_model.sh

docker-compose up --build
