import minknow_api

m = minknow_api.manager.Manager()
p = list(m.flow_cell_positions())[0]
c = p.connect()

current_info = c.protocol.get_current_protocol_run()

print(current_info)




# response = c.protocol.list_protocols()
# for protocol in response.protocols:
#     i = protocol.identifier