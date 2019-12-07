cd ~
sudo apt install gunicorn gcc python3-flask virtualenv libpq-dev python-dev postgresql libsm6 libxext6 -y
wget https://repo.anaconda.com/archive/Anaconda3-2019.10-Linux-x86_64.sh
sh Anaconda3-2019.10-Linux-x86_64.sh
source .bashrc
rm Anaconda3-2019.10-Linux-x86_64.sh
mkdir Stonks
cd Stonks
virtualenv -p python3 Stonksenv
git init
git pull https://github.com/Build-Week-Pic-Metric-3/Data-Science.git master
mkdir Stonks/assets/weights
cd Stonks/assets/weights/
wget https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/yolo.h5
cd ....
conda activate
source Stonksenv/bin/activate
pip install -r ubuntu_requirements.txt
pip install opencv-python
conda install -c conda-forge opencv
sudo mv setup_files/template.env .env
sudo nano .env
echo "Installation complete, Starting server"
nohup gunicorn -t 120 "Stonks:create_app()"&