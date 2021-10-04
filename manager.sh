export PYTHONPATH=$(pwd)/goodguy-crawl
pip install -r goodguy-crawl/requirements.txt
pip install -r requirements.txt
python goodguy-crawl/build.py
export PYTHONPATH=$(pwd)/goodguy-crawl:$(pwd)
python manager/gui.py
