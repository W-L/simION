from minknow_api.manager import Manager

"""
this is a minimal version of what aeons uses to connect to minknow
"""

device = "MS00000"
# port = 10000
manager = Manager(host="localhost") # , port=port)

# Find a list of currently available sequencing positions.
positions = list(manager.flow_cell_positions())
print(positions)
pos_dict = {pos.name: pos for pos in positions}
# index into the dict of available devices
target_device = pos_dict[device]

# connect to the device and navigate api to get output path
device_connection = target_device.connect()
current_run = device_connection.protocol.get_current_protocol_run()
run_id = current_run.run_id
out_path = current_run.output_path

print(run_id)
print(out_path)
