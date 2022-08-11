from pyguppy_client_lib.pyclient import PyGuppyClient
from pyguppy_client_lib import helper_functions

host_path = ""
port = 5555
address = f"ipc://{host_path}/{port}"
config = "dna_r9.4.1_450bps_fast"

helper_functions.get_server_information(address=address, timeout=10)
helper_functions.get_server_stats(address=address, timeout=10)

client = PyGuppyClient(address=address, config=config)
client.set_params({"priority": PyGuppyClient.high_priority})
client.connect()
print(client.connected())
