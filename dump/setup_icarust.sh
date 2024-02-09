
# general startup
alias l="ls -Flh --color"
source icarust_venv/bin/activate
HOMEDIR="/nfs/research/goldman/lukasw/simION"
export PATH="$HOMEDIR/gfatools/paf2gfa/:$PATH"
export PATH="$HOMEDIR/minimap2/:$PATH"

# start a guppy server for readfish
/usr/bin/guppy_basecall_server --config dna_r9.4.1_450bps_fast.cfg --log_path minknow_run/logs/guppy --port 5555 -x cuda:all &

# start icarust and a basecaller loop
rm -r HI/
target/release/icarust --config ../config/icarust_zymo.toml -v &
python3 ../code/basecall_loop.py --fast5 HI/icarust_zymo/zymo/fast5/ --fastq HI/fastq_pass &

# start readfish
readfish boss-runs --device D001 --experiment-name "readfish_zymo" --toml ../code/readfish_zymo.toml --port 10000
#--log-file ru_test.log &> ru.log &

# start aeons
python /Aeons/aeons_live.py @/nfs/research/goldman/lukasw/simION/config/aeons.params
#&> aeons.log &
