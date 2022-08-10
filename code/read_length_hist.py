import minknow_api
import numpy as np
from google.protobuf.json_format import MessageToDict
import argparse



def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pos', type=int, default=0)
    parser.add_argument('--min', type=int, default=0)
    parser.add_argument('--step', type=int, default=128)
    parser.add_argument('--max', type=int, default=9984)
    parser.add_argument('--symbols', type=int, default=128)
    return parser


def connect2device(pos=0):
    m = minknow_api.manager.Manager()
    p = list(m.flow_cell_positions())[pos]
    c = p.connect()
    return c


def grab_histogram_data(c, data_selection=None):
    # get id of acquisition run
    aq_runid = c.acquisition.get_current_acquisition_run().run_id
    # use id to open stream to histogram
    # define range of histogram if needed
    if data_selection:
        d = minknow_api.statistics_pb2.DataSelection()
        d.start = data_selection[0]
        d.step = data_selection[1]
        d.end = data_selection[2]
        hist_obj = c.statistics.stream_read_length_histogram(acquisition_run_id=aq_runid, data_selection=d)
    else:
        hist_obj = c.statistics.stream_read_length_histogram(acquisition_run_id=aq_runid)

    # fetch histogram data from stream
    hist_data = hist_obj.next()
    # parse data into dict
    hist_dict = MessageToDict(hist_data)
    # final parsing into arrays
    hist_ranges = np.array([int(i['end']) for i in hist_dict['bucketRanges']])
    hist_values = np.array([int(i) for i in hist_dict['histogramData'][0]['bucketValues']])
    return hist_ranges, hist_values



def ascii_hist_values(cutoffs, counts, max_symbols=50):
    # output is collected as lines in a list
    ret = []
    # cutoffs are the bin borders of the histogram
    cutoffs = np.asarray(cutoffs)
    # counts of bins in the histogram
    counts = np.asarray(counts)
    # total number of counts
    total = sum(counts)
    # normalise counts for display
    norm_counts = counts.astype(float) / counts.sum()
    # scale such that highest bar has max_symbols
    max_val = np.max(norm_counts)
    scaling_factor = max_symbols / max_val
    scaled_counts = norm_counts * scaling_factor
    # add a line for each of the bins with their respective counts
    for cutoff, original_count, scaled_count in zip(cutoffs, counts, scaled_counts):
        ret.append(" {:>8.2f} | {:<7,d} | {:s}".format(cutoff, original_count, "*" * int(scaled_count)))
    # final lines to make it look nice and report total count
    ret.append("{:s} | {:s} | {:s}".format('-' * 8, '-' * 7, '-' * 7))
    ret.append("{:>8s} | {:<7,d}".format('N=', total))
    return '\n'.join(ret)

#%%


parser = setup_parser()
args = parser.parse_args()

connection = connect2device(pos=args.pos)
cutoffs, counts = grab_histogram_data(c=connection, data_selection=(args.min, args.step, args.max))
h = ascii_hist_values(cutoffs=cutoffs, counts=counts, max_symbols=args.symbols)
print(h)


