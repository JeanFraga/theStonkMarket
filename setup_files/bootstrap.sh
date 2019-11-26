sudo yum update -y
source activate tensorflow_p36
conda install -y gunicorn flask-sqlalchemy
conda install -c conda-forge -y python-decouple python-dotenv
pip install imageai mtcnn

mkdir repo
cd repo
git init
git pull https://github.com/Build-Week-Pic-Metric-3/Data-Science.git master
mkdir Stonks/assets/weights
cd Stonks/assets/weights/
wget https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/yolo.h5
echo "Bootstrap finished!"
echo "Now Update your .env file in the repo folder!!!"
