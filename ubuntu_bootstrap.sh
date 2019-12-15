sudo apt-get update && sudo apt-get upgrade -y

sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt install ubuntu-drivers-common
sudo apt install nvidia-driver-440

sudo apt-get install apt-transport-https ca-certificates curl software-properties-common glances
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository  "deb [arch=amd64] https://download.docker.com/linux/ubuntu  $(lsb_release -cs) stable"

sudo curl -L https://github.com/docker/compose/releases/download/1.17.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

sudo apt-get update

wget https://repo.continuum.io/archive/Anaconda3-2019.10-Linux-x86_64.sh
sh Anaconda3-2019.10-Linux-x86_64.sh
source .bashrc
rm Anaconda3-2019.10-Linux-x86_64.sh
conda config --set auto_activate_base false

conda activate
conda update conda
conda update --all
conda config --append channels conda-forge

mkdir theStonkMarket
cd theStonkMarket
git clone https://github.com/Distortedlogic/theStonkMarket.git

sh dl_model.sh

sudo docker-compose up --build
