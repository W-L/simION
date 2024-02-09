import minknow_api

m = minknow_api.manager.Manager()
p = list(m.flow_cell_positions())[0]
c = p.connect()

c.protocol.stop_protocol()

