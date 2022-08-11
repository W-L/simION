import minknow_api
from time import sleep
import sys

m = minknow_api.manager.Manager()
p = list(m.flow_cell_positions())[0]
c = p.connect()

current_info = c.protocol.get_current_protocol_run()

# from minknow_api/protocol.proto
phase_dict = {
    0: "PHASE_UNKNOWN",
    1: "PHASE_INITIALISING",
    2: "PHASE_SEQUENCING",
    3: "PHASE_PREPARING_FOR_MUX_SCAN",
    4: "PHASE_MUX_SCAN",
    5: "PHASE_PAUSED",
    6: "PHASE_PAUSING",
    7: "PHASE_RESUMING"}

print(current_info.args)
print()
print(current_info.run_id)
print(current_info.protocol_id)
print(current_info.output_path)
print(current_info.output_path.split('/')[-1])
print()


while True:
    current_info = c.protocol.get_current_protocol_run()
    cphase = phase_dict[current_info.phase]
    print(cphase)
    if cphase != "PHASE_SEQUENCING":
        sleep(10)
    else:
        sys.exit()



# response = c.protocol.list_protocols()
# for protocol in response.protocols:
#     i = protocol.identifier