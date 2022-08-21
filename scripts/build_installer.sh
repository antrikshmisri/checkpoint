# build `ui/setup/install.py` using pyinstaller, use console mode

echo "setting up venv"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


echo "Building installer..."
pyinstaller --onefile --windowed --noconfirm --clean --workpath=build --distpath=dist --name=$1 install.py