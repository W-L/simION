# wrapper to launch playback run in singularity container
# launch minknow and guppy servers
pkill mk_manager
pkill guppy
sleep 5
/opt/ont/minknow/bin/mk_manager_svc --simulated-minion-devices 1 -d &
sleep 10
echo "Initiated minknow server"
/usr/bin/guppy_basecall_server --config dna_r9.4.1_450bps_fast.cfg --log_path minknow_run/logs/guppy --port 5555 -x cuda:all --verbose_logs &
sleep 5
echo "Initiated guppy server"
# remove --fastq and --basecalling for playback without live basecalling
python3 /code/start_minknow_run.py --position MS00000 --kit SQK-RAD004 --fast5 --fastq --basecalling
sleep 2
# this loops to wait until actual sequencing has started
# PHASE INIT, PHASE MUX_SCAN, PHASE SEQUENCING
python3 /code/query_minknow_run.py


