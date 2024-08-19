# simION

This project started out as a guide to run playback ONT sequencing without sudo or a GUI.
Now I have sudo permissions on a VM with a GPU and a GUI, so this guide will be much simplified.
For the previous instructions, see the directory `arch/`.

DISCLAIMER: You need to be part of the ONT community forum to be able to use this repository. Check their policies and how to get an account on the platform.



## Setup

- log into PVE to start VM
- ssh into VM 
- run scripts to install software and setup the project's environment
- (setup deployment via pycharm to get WIP code in VM)


```shell
sudo apt-get update
sudo apt-get install git curl htop

mkdir -p ~/proj/simion && cd ~/proj/simion
echo 'alias l="ls -Flh --color"' >>~/.bash_aliases 
echo 'alias les="less -S"' >>~/.bash_aliases
source ~/.bash_aliases
# INSTALL ONT SOFTWARE
# grab and add the public key for the ONT repos
wget -O ont_key https://cdn.oxfordnanoportal.com/apt/ont-repo.pub
sudo apt-key add ont_key
# add the repository to the sources and update lists
echo "deb http://cdn.oxfordnanoportal.com/apt focal-stable non-free" | sudo tee /etc/apt/sources.list.d/nanoporetech.sources.list
sudo apt-get update
# install ONT's software - and a huge dependency tree
sudo apt-get install -y ont-standalone-minknow-gpu-release

# download bulk fast5 file for playback sequencing
mkdir -p ~/proj/simion/data
wget https://s3.amazonaws.com/nanopore-human-wgs/bulkfile/GXB02001_20230509_1250_FAW79338_X3_sequencing_run_NA12878_B1_19382aa5_ef4362cd.fast5 -O ./data/GXB02001_20230509_1250_FAW79338_X3_sequencing_run_NA12878_B1_19382aa5_ef4362cd.fast5


# install miniforge
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

At this point a quick logging out/in is necessary to make mamba happy

```shell
# create mamba env in which to run the playback 
mamba create -n simion
mamba activate simion
mamba install python==3.11 pip bioconda::gfatools bioconda::minimap2 bioconda::miniasm bioconda::mappy
pip install minknow_api
# requirements for boss testing
pip install pytest-cov pytest-timeout numba scipy bottleneck 

# download and index human genome
BOSS_DATA_DIR=~/proj/boss/BOSS-RUNS/data
wget https://ftp.ensembl.org/pub/release-112/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz -O $BOSS_DATA_DIR/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
gunzip $BOSS_DATA_DIR/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
minimap2 -x map-ont -d $BOSS_DATA_DIR/Homo_sapiens.GRCh38.dna.primary_assembly.fa.mmi $BOSS_DATA_DIR/Homo_sapiens.GRCh38.dna.primary_assembly.fa

# adjust permissions of various ONT files
sudo chmod -R a+w /opt/ont/dorado/data
sudo chmod a+w /opt/ont/minknow/conf/app_conf
sudo chmod a+w /opt/ont/minknow/conf/user_conf
sudo chmod a+w /opt/ont/minknow/conf/package/sequencing/sequencing_MIN114_DNA_e8_2_400K.toml
sudo chmod a+rwx /tmp/.guppy/
sudo chmod 4755 /opt/ont/ui/kingfisher/chrome-sandbox
```


## stop ONTs daemons


```shell
# code snippet that's useful when running minknow NOT in singularity
# stop and disable the systemctl services, launch manually when needed instead
systemctl stop doradod.service
systemctl disable doradod.service
systemctl stop minknow.service
systemctl disable minknow.service
````
    


## setup ONT configs

Necessary changes to the ONT config files for playback sequencing.
Main action here is to point to a bulkfile for playback. 
I.e. write the `simulation = []` line to the sequencing protocol.toml
This might not be necessary if using a GUI, then playback can be selected in MinKNOW

```shell
# make a backup copy of the sequencing protocol
cp /opt/ont/minknow/conf/package/sequencing/sequencing_MIN114_DNA_e8_2_400K.toml /opt/ont/minknow/conf/package/sequencing/sequencing_MIN114_DNA_e8_2_400K.toml.bkp
# add the line to point to a bulkfile for simulation 
sed -i '/\[custom_settings\]/a simulation="/home/administrator/proj/simion/data/GXB02001_20230509_1250_FAW79338_X3_sequencing_run_NA12878_B1_19382aa5_ef4362cd.fast5"' /opt/ont/minknow/conf/package/sequencing/sequencing_MIN114_DNA_e8_2_400K.toml
# change output directory of minknow in user config, and lower minimum disk space. Otherwise sequencing might not work
/opt/ont/minknow/bin/config_editor --conf user --filename /opt/ont/minknow/conf/user_conf --set output_dirs.logs="logs" --set output_dirs.base="$(pwd)/minknow_run"
/opt/ont/minknow/bin/config_editor --conf application --filename /opt/ont/minknow/conf/app_conf --set disk_space_warnings.reads.minimum_space_mb=1000 
```


## Playback procedure

 
```shell
mamba activate simion
cd ~/proj/simion
bash code/launch_playback.sh   

cd ~/proj/boss/BOSS-RUNS/tests

# 1. test readfish on its own - unblock everything 
readfish unblock-all --device MS00000 --experiment-name "rf_uall"

# 2. test integrated readfish
# with this config, roughly half of all reads should be rejected,
# i.e. all reads from runs conditionn
python ../boss/readfish_boss.py config/BOSS_RUNS_RF.toml MS00000 boss
python trigger_updates.py out_runs/
python ../boss/readfish_boss.py config/BOSS_AEONS_RF.toml MS00000 boss
python trigger_updates.py out_aeons/

# 3. run boss on the sample configs
python ../boss/BOSS.py --toml config/BOSS_AEONS.toml --toml_readfish config/BOSS_AEONS_RF.toml  
python ../boss/BOSS.py --toml config/BOSS_RUNS_CH20.toml --toml_readfish config/BOSS_RUNS_RF.toml 


# 4. run the playback pytests
pytest playback


# summary of read lengths per target chromosome
# readfish summary code/human_chr_selection.toml minknow_run/no_group/no_sample/20220811_2302_MS00000__674e6c81/fastq_pass/
python code/read_length_hist.py
python code/stop_minknow_run.py
```










## Maintenance notes

Bits that might change in the future and need to be checked:
- ONT software stack: update installation commands in setup script
- sequencing protocol: change in code block of ONT configs; change in start_protocol_mod.py
- sequencing kit: in launch_playback.sh; in start_protocol_mod.py
- starting protocol from api: start_protocol.py from their examples. All changes in my version are marked with TODOs
- minknow_api: update the script to start sequencing - start_protocol_mod.py has hard-coded protocol


## Acknowledgements

Crucial resources: 

[Miles Benton's](https://github.com/sirselim) guides for live GPU basecalling:

* https://hackmd.io/@Miles/ryVAI_KWF#install-MinKNOW-and-required-packages

* https://github.com/sirselim/jetson_nanopore_sequencing/blob/main/live_basecalling.md

starting a head-less sequencing run:

- lightly modified version of [minknow_api's example `start_protocol.py`](https://github.com/nanoporetech/minknow_api/blob/9302ac463827fc492e6d5fa80c29f56707ca7984/python/minknow_api/examples/start_protocol.py), licensed under MPL2.0


