from minknow_api.manager import Manager
import subprocess
import shlex


m = Manager()
p = list(m.flow_cell_positions())[0]
c = p.connect()

c.protocol.stop_protocol()


#dor = subprocess.run(shlex.split("pkill dorado"), capture_output=True, text=True)
#print(dor.stdout)
#print(dor.stderr)
#mkm = subprocess.run(shlex.split("pkill mk_manager"), capture_output=True, text=True)
#print(mkm.stdout)
#print(mkm.stderr)
#mkw = subprocess.run(shlex.split("pkill minknow"), capture_output=True, text=True)
#print(mkw.stdout)
#print(mkw.stderr)

