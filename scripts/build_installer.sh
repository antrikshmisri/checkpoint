# build `ui/setup/install.py` using pyinstaller, use console mode
# check if venv is present, if not setup venv using `python3 -m venv venv` and install dependencies

if [ ! -d "venv" ]; then
    echo "venv not found, setting up venv"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "venv found, activating"
    source venv/bin/activate
fi

echo "Building installer..."
pyinstaller --onefile --windowed --noconfirm --clean --workpath=build --distpath=dist --name=$1 install.py