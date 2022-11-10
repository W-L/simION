

/usr/bin/guppy_basecall_server --config dna_r9.4.1_450bps_fast.cfg --log_path minknow_run/logs/guppy --port 5555 -x cuda:all &

target/release/icarust --config Profile_tomls/config.toml -v &

python3 code/basecall_loop.py

readfish boss-runs --device Bantersaurus --experiment-name "rf001" --toml ../code/readfish_zymo.toml


--log-file ru_test.log &> ru.log &

