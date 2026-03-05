import os
import sys

file=sys.argv[1]

print(os.access(file, os.W_OK))
