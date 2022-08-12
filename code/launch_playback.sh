# wrapper to prepare and launch playback run in the singularity container

# change output directory of minknow in config - needs pwd
/opt/ont/minknow/bin/config_editor --conf user --filename /opt/ont/minknow/conf/user_conf --set output_dirs.logs="logs" --set output_dirs.base="$(pwd)/minknow_run"
/opt/ont/minknow/bin/config_editor --conf application --filename /opt/ont/minknow/conf/app_conf --set guppy.connection.server_ipc_file="$(pwd)/5555"
# edit toml file for host - replace host line with port sitting at pwd
sed -i "s#.*host.*#host\ =\ \"ipc://$(pwd)\"#" code/human_chr_selection.toml
# for runtime, launch the minknow and guppy servers
/opt/ont/minknow/bin/mk_manager_svc --simulated-minion-devices 1 -d &
sleep 10
echo "Initiated minknow server"
/usr/bin/guppy_basecall_server --log_path /var/log/guppy --config dna_r9.4.1_450bps_fast.cfg --port 5555 -x cuda:all &
sleep 5
echo "Initiated guppy server"
# load the venv and start a sequencing run via the api
source /bossruns/bin/activate
# remove --fastq and --basecalling for playback without live basecalling
python3 /code/start_minknow_run.py --position MS00000 --kit SQK-RAD004 --fast5 --fastq --basecalling
sleep 2
# wait until actual sequencing has started
python3 /code/query_minknow_run.py


