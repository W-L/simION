# simION

Running playback ONT sequencing without sudo or a GUI. 
This is intended for testing software that interacts with sequencing runs on a system where a user does not have sudo permissions or access to the MinKNOW GUI, e.g. 
a HPC with GPUs for live basecalling.


## Setup

The playback sequencing is run inside a singularity container, defined in `code/simION.def`.

The HPC system needs to have nvidia drivers & cuda installed for the available GPUs. 
The cuda version needs to be adapted at the top of the singularity definition file.


The container needs to be built locally with sudo and transferred to the HPC

```shell
sudo singularity build -F simION.sif code/simION.def && scp simION.sif user@HPC:/destination/path
```

To save the sequencing output from within the container we need to overlay a file system image.
This can be created with 

```shell
singularity exec docker://ubuntu:18.04 bash -c "mkdir -p overlay/upper overlay/work &&
                                                dd if=/dev/zero of=overlay.img count=200 bs=1M &&
                                                mkfs.ext3 -d overlay overlay.img && 
                                                rm -r overlay/"
```


## Required data

The container does not have all files included to make it smaller.
These files need to be bind mounted when running the container:

- bulkfile for playback
- minimap-index of the used reference


e.g.: store all files in `./data` and mount with argument `-B data/:/data`. 
This makes the files available in the container at `/data`.


## Usage

Once the container is production-state it can be `exec`ed. 

For now, launch a shell with:

- `--nv` to load GPU drivers
- `--overlay overlay.img` add the overlay file system
- `-B` bind mount the data and code directories


```shell
singularity shell --nv -B data/:/data -B code/:/code --overlay overlay.img simION.sif
```

then run the `%runscript` portion manually in the shell


## Other bits and log files

log of the sequencing protocol
`less minknow_run/logs/MS00000/control_server_log-0.txt`

fastq drop-off
`l minknow_run/no_group/no_sample/20220811_1701_MS00000__b3e4edf9/fastq_pass/`


## Acknowledgements

Crucial resources: 

[Miles Benton's](https://github.com/sirselim) guides for live GPU basecalling:

* https://hackmd.io/@Miles/ryVAI_KWF#install-MinKNOW-and-required-packages

* https://github.com/sirselim/jetson_nanopore_sequencing/blob/main/live_basecalling.md

starting a head-less sequencing run:

- lightly modified version of [minknow_api's example `start_protocol.py`](https://github.com/nanoporetech/minknow_api/blob/9302ac463827fc492e6d5fa80c29f56707ca7984/python/minknow_api/examples/start_protocol.py), licensed under MPL2.0


