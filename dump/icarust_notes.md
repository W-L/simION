# ICARUST

- runs as single CL binary with a config toml file
- places fast5 files into a specified output dir


## setting up icarust in singularity

- definition file with base ubuntu, cuda, ONT stack, py3.8
- icarust itself gets installed in a shell of the container, not during building

```shell
sudo singularity build -F icarust.sif code/icarust.def
scp icarust.sif lukasw@codon:/nfs/research/goldman/lukasw/simION
````


## install icarust

```shell
bash install_icarust.sh
```

might need some edits before compilation
- main.rs: correct path to ONT certs
- config.toml: correct squiggles etc.


## runtime

```shell
interact_gpu_vhi
source ~/.bash_aliases
singularity shell --nv -B /nfs/research/goldman/lukasw/aeons/Aeons/:/Aeons --overlay overlay_aeons.img icarust.sif

```


```shell
setup_ont_configs.sh
setup_environment.sh
setup_icarust.sh
```


