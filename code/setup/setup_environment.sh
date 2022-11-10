# setup venv
python3 -m venv icarust-venv
source icarust-venv/bin/activate

# install pip stuff
pip install --upgrade pip
pip install git+https://github.com/nanoporetech/read_until_api@v3.0.0
pip install git+https://github.com/W-L/readfish@issue208
apt list --installed ont-guppy* | tail -n 1 | cut -f2 -d' ' | cut -f1 -d'-' >guppy_version
pip install ont_pyguppy_client_lib==$(cat guppy_version)
pip install ont_fast5_api

# aeons dependencies
HOMEDIR="/nfs/research/goldman/lukasw/simION"
cd $HOMEDIR && git clone https://github.com/lh3/gfatools
cd gfatools/paf2gfa && make
cd $HOMEDIR && git clone https://github.com/lh3/minimap2
cd minimap2 && make
# add dependencies to path
export PATH="$HOMEDIR/gfatools/paf2gfa/:$PATH"
export PATH="$HOMEDIR/minimap2/:$PATH"

