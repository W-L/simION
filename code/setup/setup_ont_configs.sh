/opt/ont/minknow/bin/config_editor --conf application --filename /opt/ont/minknow/conf/app_conf --set guppy.server_config.server_executable="/opt/ont/guppy/bin/guppy_basecall_server" --set guppy.client_executable="/opt/ont/guppy/bin/guppy_basecall_client" --set guppy.server_config.gpu_calling=1 --set guppy.server_config.num_threads=16 --set guppy.server_config.ipc_threads=2 --set guppy.server_config.chunks_per_runner=160
# the bulk file needs to be bind mounted when the container is invoked
sed -i '/\[custom_settings\]/a simulation="/data/GXB02001_20190822_081457_FAL00432_gridion_sequencing_run_zymo_gradual_reject_40x_hac_post_control.fast5"' /opt/ont/minknow/conf/package/sequencing/sequencing_MIN106_DNA.toml
sed -i 's/break_reads_after_seconds\ =\ 1.0/break_reads_after_seconds\ =\ 0.4/' /opt/ont/minknow/conf/package/sequencing/sequencing_MIN106_DNA.toml


# change output directory of minknow in config - needs pwd
/opt/ont/minknow/bin/config_editor --conf user --filename /opt/ont/minknow/conf/user_conf --set output_dirs.logs="logs" --set output_dirs.base="$(pwd)/minknow_run"
/opt/ont/minknow/bin/config_editor --conf application --filename /opt/ont/minknow/conf/app_conf --set guppy.connection.server_ipc_file="$(pwd)/5555"
