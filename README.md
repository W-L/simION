# simION

Running playback ONT sequencing without sudo or a GUI. 
For testing software that interacts with sequencing runs on a system where a user does not have sudo or access to the MinKNOW GUI,
e.g. a HPC with GPUs for live basecalling.

You need to be part of the ONT community forum to be able to use this repository. Check their policies and how to get an account on the platform.


# Workflow

## Setup

The playback sequencing is run in a shell spawned from a singularity container.
This means you need to build the singularity container in an environment where you have sudo. 
(I use singularityCE in conda for building)
The system where you want to run playback sequencing needs a GPU with nvidia drivers and cuda installed. And you'll need conda on the host machine as well.
The cuda version needs to be adapted at the top of the singularity definition file before building the container.

The container definition is at `code/00_definitions/simION.def`

command for building the container locally with sudo and transferring to HPC

```shell
sudo singularity build -F simION.sif code/00_definitions/simION.def && scp simION.sif user@HPC:/destination/path
```

Alternatively (not recommended) build a sandbox, enter shell and install things manually for testing

```shell
sudo singularity build --sandbox simION_sandbox code/00_definitions/simION_sandbox.def
sudo singularity shell -B code:/root/code -B data:/root/data --writable simION_sandbox
```



## First-time container setup


Make sure you are on an interactive GPU node and singularity is available (e.g. module load singularity-XX) 

Some files need to be bind-mounted when running the container:

- bulkfile for playback
- boss* code for testing
- fasta and minimap-index of the used reference (BOSS-RUNS)

e.g. store all files in `./data` and mount with argument `-B data/:/root/data`. 
This makes the files available in the container at `/root/data`.

To save output data, use an overlay file system (host FS is read-only in singularity container). 

`singularity overlay create --size 20480 overlay.img`


```shell
singularity shell --nv -B ../BR/BOSS-RUNS:/root/BOSS-RUNS --overlay overlay.img simION.sif
```

Install boss-runs (incl readfish and some extra dependencies)


```shell
micromamba create -n boss python=3.10 pip gfatools minimap2 miniasm && micromamba activate boss
pip install dist/boss_runs-0.1.0-py3-none-any.whl
```


## setup ONT configs

Necessary changes to the ONT config files for playback sequencing. Main action here is to point to a bulkfile for playback. 
I.e. writes the `simulation = []` line to the sequencing protocol.toml
You can get a bulkfile from the readfish repository and then change the path in the next code snippet

```shell
# make a backup copy of the sequencing protocol
cp /opt/ont/minknow/conf/package/sequencing/sequencing_MIN114_DNA_e8_2_400K.toml /opt/ont/minknow/conf/package/sequencing/sequencing_MIN114_DNA_e8_2_400K.toml.bkp
# add the line to point to a bulkfile for simulation 
# this is still needed despite the playback option that exists in the GUI now
# CHANGE THE PATH TO THE BULKFILE HERE
sed -i '/\[custom_settings\]/a simulation="/path/to/bulkfile.fast5"' /opt/ont/minknow/conf/package/sequencing/sequencing_MIN114_DNA_e8_2_400K.toml
# for convenience: change output directory of minknow in user config
/opt/ont/minknow/bin/config_editor --conf user --filename /opt/ont/minknow/conf/user_conf --set output_dirs.logs="logs" --set output_dirs.base="$(pwd)/minknow_run"
```



## Playback procedure

 These are the commands to run playback sequencing. Some of these are specific to the HPC system I work on and will need to be adjusted.  

```shell
# get an interactive job on a node with A100 GPU and load singularity module
bsub -q gpu-a100 -gpu "num=1:gmem=8000" -M 32G -n 4 -Is $SHELL
module load singularity-3.8.7-gcc-11.2.0-jtpp6xx
# enter container with mounting code etc.
singularity shell --nv -B ../BR/BOSS-RUNS:/root/BOSS-RUNS --overlay overlay.img simION.sif
alias l="ls -Flh --color" && alias les="less -S"
./bin/micromamba shell init --shell bash --root-prefix=~/micromamba && eval "$(./bin/micromamba shell hook --shell bash -p ~/micromamba)" 
micromamba activate boss
cd testing
# launch playback
bash ../code/01_playback/launch_playback.sh   

# Now the playback sequencing is running other software can be tested

# for example: to test readfish on its own - unblock everything 
 readfish unblock-all --device MS00000 --experiment-name "rf_uall"
# look at rejection peak to confirm outcome
 python code/read_length_hist.py


# this is the main log of the playback protocol
less minknow_run/logs/MS00000/control_server_log-0.txt
# to stop the playback 
python ../code/01_playback/stop_minknow_run.py
```





## Maintenance notes

Bits that might change in the future and need to be checked:
- cuda version on the cluster: change the base of the singularity container
- ONT software stack: update installation commands in container build script
- sequencing protocol: update in build script; change in code block of ONT configs; change in start_protocol_mod.py
- sequencing kit: in launch_playback.sh; in start_protocol_mod.py
- starting protocol from api: start_protocol.py from their examples. All changes in my version are marked with TODOs 
- path to bulkfile for playback: specified in ONT config code block
- minknow_api: update the script to start sequencing - start_protocol_mod.py has hard-coded protocol


## Acknowledgements

Crucial resources: 

[Miles Benton's](https://github.com/sirselim) guides for live GPU basecalling:

* https://hackmd.io/@Miles/ryVAI_KWF#install-MinKNOW-and-required-packages

* https://github.com/sirselim/jetson_nanopore_sequencing/blob/main/live_basecalling.md

starting a head-less sequencing run:

- lightly modified version of [minknow_api's example `start_protocol.py`](https://github.com/nanoporetech/minknow_api/blob/9302ac463827fc492e6d5fa80c29f56707ca7984/python/minknow_api/examples/start_protocol.py), licensed under MPL2.0


