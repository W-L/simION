import subprocess
import logging
import argparse
from datetime import datetime
from time import sleep
from shutil import which
from sys import executable
from pathlib import Path
import os


def setup_parser():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('--fast5', dest='fast5', type=str, default=None, help='directory of fast5 files')
    parser.add_argument('--fastq', dest='fastq', type=str, default=None, help='directory for basecalled fastqs')
    parser.add_argument('--port', dest='port', type=str, default="5555", help='port of basecaller')
    parser.add_argument('--interval', dest='interval', type=int, default=30, help='seconds between basecalling')
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

    def __init__(self, fast5, fastq, port):
        self.fast5 = Path(fast5)
        self.fastq = Path(fastq)
        if not os.path.exists(self.fastq):
            os.mkdir(self.fastq)

        self.base_dir = self.fast5.parent
        self.guppy_dir = self.base_dir / 'fastq_calling'
        self.port = port

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
        logfile = f"log_basecall_{timestamp}.log"
        logging.basicConfig(format='%(asctime)s %(message)s',
                            level=logging.INFO,
                            handlers=[logging.FileHandler(f"{logfile}")])

        self.guppy = find_exe("guppy_basecaller")
        # execute(f"rm -r {self.fastq_dir}")


    def launch_caller(self, resume=False):
        comm = f"{self.guppy} "
        comm += f"-i {self.fast5} "
        comm += f"--save_path {self.guppy_dir} "
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


    def move_called_files(self):
        comm = f"mv {self.guppy_dir}/pass/*.fastq.gz {self.fastq}/"
        logging.info(comm)
        stdout, stderr = execute(comm)
        logging.info(stdout)
        logging.info(stderr)



def main():
    parser = setup_parser()
    args = parser.parse_args()
    # initiate basecaller
    bc = BaseCaller(fast5=args.fast5, fastq=args.fastq, port=args.port)
    # launch once outside of loop
    bc.launch_caller()
    sleep(args.interval)
    while True:
        # launch periodically with --resume
        bc.launch_caller(resume=True)
        bc.move_called_files()
        sleep(args.interval)


if __name__ == '__main__':
    main()


