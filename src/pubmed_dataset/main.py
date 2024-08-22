#!/usr/bin/env python3

'''
Fetch and format the pubmed-diabetes dataset via the Pubmed API
'''

import os
import io
import sys
import logging
import argparse

import pandas as pd

from .benchmark import get_pubmed_dataset
from .entryset import EntrySet


logger = logging.getLogger(__name__)


def parse_args():
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    parser = argparse.ArgumentParser(description='Pull pubmed data')
    parser.add_argument('--loglevel', '-l', choices=log_levels,
                        default='INFO', help='Logging verbosity level')
    parser.add_argument('--progress', '-p', action='store_true',
                        help='Display a progress bar')

    parser.add_argument('--infile', '-i', default=None,
                        help='Optional file containing a newline-separated list of PMIDs to pull (if not provided, use pubmed benchmark)')
    parser.add_argument('outdir', default='output', help='Output directory')

    return parser.parse_args()


def log_setup(log_level):
    ll = getattr(logging, log_level)
    fmt = '%(asctime)s : %(levelname)s : %(message)s'

    logging.basicConfig(format=fmt, level=ll)


def main():
    args = parse_args()

    log_setup(args.loglevel)
    os.makedirs(args.outdir, exist_ok=True)

    if not args.infile:
        nodes, cites = get_pubmed_dataset(args.infile)
        pmids = nodes['node_id'].tolist()
    else:
        if args.infile == '-':
            pmids = sys.stdin.readlines()
        else:
            with open(args.infile, 'rt', encoding='utf-8') as f:
                pmids = f.readlines()

        pmids = list(map(int, input_data))

    files = EntrySet(
        pmids,
        cache_dir=os.path.join(args.outdir, 'cache'),
        progress=args.progress,
    ).populate().to_pandas()

    if not args.infile:  # pubmed benchmark, include its data
        files['node-data'] = files['node-data'].merge(
            nodes, how='left', on='node_id'  # keep the human annotations
        )

        cites['cites'] = 1
        files['graph']['new'] = 1
        files['graph'] = files['graph'].merge(cites, how='outer') \
            .fillna(0) \
            .astype(int)

    for k, v in files.items():
        v.to_csv(f'{args.outdir}/{k}.csv', index=False, sep='\t')


if __name__ == '__main__':
    main()
