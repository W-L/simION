pkill mk_manager
pkill minknow
sleep 5
pkill dorado
sleep 5

dorado_basecall_server -x cuda:all -c /opt/ont/dorado/data/dna_r10.4.1_e8.2_400bps_5khz_fast.cfg -p ipc:///tmp/.guppy/5555 -l minknow_run/logs/dorado --verbose_logs &
sleep 5 && echo "Initiated basecall server"
/opt/ont/minknow/bin/mk_manager_svc -c /opt/ont/minknow/conf --simulated-minion-devices=1 -d &
sleep 10 && echo "Initiated minknow server"

python3 code/start_protocol_mod.py --position MS00000 --kit SQK-LSK114 --pod5 --fastq --basecalling --fastq-reads-per-file 1000 --pod5-reads-per-file 1000

sleep 2
python3 code/query_minknow_run.py
python3 code/read_length_hist.py

