# py -3 -m venv aazdev
# ./aazdev/Scripts/Activate

cd ./src/web
npm install
npm run build

cd ../backend
pip install -r ./requirements.txt
pip install -e .