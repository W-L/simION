# Setting up playback on machine with sudo & GUI

This is for a basic playback setup without live base calling


## Installation

```shell
# add public key for ONT repos
wget -O ont_key https://mirror.oxfordnanoportal.com/apt/ont-repo.pub
sudo apt-key add ont_key

# add repo to sources
echo "deb http://mirror.oxfordnanoportal.com/apt focal-stable non-free" | sudo tee /etc/apt/sources.list.d/nanoporetech.sources.list
sudo apt update
# test package archive
apt policy minknow-core-minion-nc 

# install ont software stack
sudo apt install minion-nc

# stop and disable the systemctl services
# launch these manually when needed
systemctl stop guppyd.service
systemctl disable guppyd.service
systemctl stop minknow.service
systemctl disable minknow.service

# add line to protocol file at [custom_settings]
# file path: /opt/ont/minknow/conf/package/sequencing/sequencing_MIN106_DNA.toml
# addition: simulation = "/full/path/to/your_bulk.FAST5"

# start minknow system process with a simulated device
sudo /opt/ont/minknow/bin/mk_manager_svc --simulated-minion-devices 1
```


## Usage

- launch MinKNOW GUI
- login with nanopore account
- reload scripts in GUI
- set up sequencing run with modified run protocol


# API usage

Alternatively, the api can be used to launch experiments without a GUI
- for this, the toml file needs to be overwritten instead of a new one with different name
- also need either lots of free space or change of the mem limits in app_conf
- if the api script does not find the correct protocol, it can be hard-coded to select the correct one

```shell
# launch with example script
python ~/software/minknow_api/python/minknow_api/examples/start_protocol.py --position MS00000 --kit SQK-RAD004 --fast5
```


basics to connect to the sequencing position with the API
```python
m = minknow_api.manager.Manager()
pos = list(m.flow_cell_positions())
ms = pos[0]
c = ms.connect()
fci = c.device.get_flow_cell_info()
```

# issues

permission problem: minknow output directory is not writeable for my own user
- hack: chmod -R o+w OUTDIR


# GPU usage on cluster

for live base calling a GPU is needed. For cluster usage in LSF:
Request an interactive job on the gpu queue - needs extra flag to reserve the gpu device
GPU availability can be tested with `./cuda_test`


```shell
alias interact_gpu='bsub -q gpu-a100 -gpu "num=1:gmem=1000" -M 8G -n 1 -Is $SHELL'
```





