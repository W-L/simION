import subprocess
import logging
import argparse
from datetime import datetime
from time import sleep
from shutil import which
from sys import executable


def setup_parser():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('--fast5', dest='fast5', type=str, default=None, help='directory of fast5 files')
    parser.add_argument('--port', dest='port', type=str, default="5555", help='port of basecaller')                                                    # OPT
    return parser


def find_exe(name):
    # shutil.which seems to work mostly but is still not completely portable
    exe = which(name, path='/'.join(executable.split('/')[0:-1]))
    if not exe:
        exe = which(name)
    if not exe:
        exe = subprocess.run(f'which {name}', shell=True, capture_output=True, universal_newlines=True).stdout
    if not exe:
        return
    return exe.strip()


def execute(command):
    # create the unix process
    running = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               encoding='utf-8',
                               shell=True)
    # run on a shell and wait until it finishes
    stdout, stderr = running.communicate()
    return stdout, stderr


class BaseCaller:

    def __init__(self, watched_dir, port):
        self.watched_dir = watched_dir
        self.port = port

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
        logfile = f"log_basecall_{timestamp}.log"
        logging.basicConfig(format='%(asctime)s %(message)s',
                            level=logging.INFO,
                            handlers=[logging.FileHandler(f"{logfile}"), logging.StreamHandler()])

        self.guppy = find_exe("guppy_basecaller")
        self.out_path = "fastq_out/"
        execute(f"rm -r {self.out_path}")


    def launch_caller(self, resume=False):
        comm = f"{self.guppy} "
        comm += f"-i {self.watched_dir} "
        comm += f"--save_path {self.out_path} "
        comm += "-x cuda:all "  # this is to select GPU calling when spinning up own server
        comm += "-c /opt/ont/guppy/data/dna_r9.4.1_450bps_fast.cfg "
        comm += "--disable_pings --compress_fastq "
        # comm += f"--port ipc://{os.getcwd()}/{self.port} "
        # comm += "--num_clients 4 -r "
        if resume:
            comm += "--resume "

        logging.info(comm)
        stdout, stderr = execute(comm)
        logging.info(stdout)
        logging.info(stderr)


def main():
    parser = setup_parser()
    args = parser.parse_args()
    # initiate basecaller
    bc = BaseCaller(watched_dir=args.fast5, port=args.port)
    # launch once outside of loop
    bc.launch_caller()
    sleep(10)
    while True:
        # launch periodically with --resume
        bc.launch_caller(resume=True)
        sleep(10)


if __name__ == '__main__':
    main()


