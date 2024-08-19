: '
wrapper to launch playback run in singularity container

1 start a simulated device using mk_manager_svc

2 launch basecall server  config: dna_r10.4.1_e8.2_400bps_5khz_fast.cfg

3 start minknow run
    - with simulated position MS00000
    - kit SQK-LSK114
    - base protocol: /opt/ont/minknow/conf/package/sequencing/sequencing_MIN114_DNA_e8_2_400K.toml

4 - query status and wait until run started
'


# launch minknow and basecall server
pkill mk_manager
pkill minknow
sleep 5
pkill dorado
sleep 5

/opt/ont/dorado/bin/dorado_basecall_server -x cuda:all -c /opt/ont/dorado/data/dna_r10.4.1_e8.2_400bps_5khz_fast.cfg -p ipc:///tmp/.guppy/5555 -l ../minknow_run/logs/dorado --verbose_logs &
# NO GPU (testing)
#/opt/ont/dorado/bin/dorado_basecall_server -c /opt/ont/dorado/data/dna_r10.4.1_e8.2_400bps_5khz_fast.cfg -p ipc:///tmp/.guppy/5555 -l ../minknow_run/logs/dorado --verbose_logs &

sleep 5
echo "Initiated basecall server"
/opt/ont/minknow/bin/mk_manager_svc -c /opt/ont/minknow/conf --simulated-minion-devices=1 -d &
sleep 10
echo "Initiated minknow server"

python3 ../code/01_playback/start_protocol_mod.py --position MS00000 --kit SQK-LSK114 --pod5 --fastq --basecalling --fastq-reads-per-file 1000 --pod5-reads-per-file 1000
# NO GPU (testing)
#python3 ../code/01_playback/start_protocol_mod.py --position MS00000 --kit SQK-LSK114 --pod5

sleep 2
# this loops to wait until actual sequencing has started - takes a couple of minutes
# PHASE INIT -> PHASE MUX_SCAN -> PHASE SEQUENCING
python3 ../code/01_playback/query_minknow_run.py
# finish by displaying the histogram of read lengths sequenced so far
python3 ../code/read_length_hist.py
# then the playback keeps running....

