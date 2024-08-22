import io
import zipfile
import logging
import importlib

import pandas as pd


logger = logging.getLogger(__name__)


def get_pubmed_dataset(path):
    NODE_PATH = 'pubmed-diabetes/data/Pubmed-Diabetes.NODE.paper.tab'
    GRAPH_PATH = 'pubmed-diabetes/data/Pubmed-Diabetes.DIRECTED.cites.tab'
    ZIP_PATH = 'pubmed-diabetes.zip'

    with importlib.resources.open_binary('pubmed_dataset.data', ZIP_PATH) as zf_bytes:
        with zipfile.ZipFile(io.BytesIO(zf_bytes.read())) as zf:
            with io.TextIOWrapper(zf.open(NODE_PATH), encoding='utf-8') as f:
                nodes = pd.read_csv(f, sep='\t', skiprows=1, low_memory=False)

            with io.TextIOWrapper(zf.open(GRAPH_PATH), encoding='utf-8') as f:
                cites = pd.read_csv(
                    f, sep='\t', skiprows=2,
                    names=['c1', 'source', 'c3', 'target']
                )

    nodes = nodes[nodes.columns[0:2].tolist()]
    nodes.columns = ['node_id', 'label']  # node_id == Pubmed's pmid
    nodes['label'] = nodes['label'].str.replace('label=', '').astype(int)
    nodes = nodes.sample(frac=1)  # fetch in random order to help debugging

    cites = cites.drop(['c1', 'c3'], axis=1)
    cites['source'] = cites['source'].str.replace('paper:', '').astype(int)
    cites['target'] = cites['target'].str.replace('paper:', '').astype(int)

    # this article is no longer on pubmed - retracted or something?
    nodes = nodes.loc[nodes['node_id'] != 17874530, :]

    mask = ((cites['source'] != 17874530) & (cites['target'] != 17874530))
    cites = cites.loc[mask, :]

    return nodes, cites


def new_pubmed_dataset():
    ZIP_PATH = 'pubmed-new.zip'

    with importlib.resources.open_binary('pubmed_dataset.data', ZIP_PATH) as zf_bytes:
        with zipfile.ZipFile(io.BytesIO(zf_bytes.read())) as zf:
            ret = {}

            with io.TextIOWrapper(zf.open('graph.csv'), encoding='utf-8') as f:
                ret['graph'] = pd.read_csv(f, sep='\t')

            with io.TextIOWrapper(zf.open('texts.csv'), encoding='utf-8') as f:
                ret['texts'] = pd.read_csv(f, sep='\t')

            with io.TextIOWrapper(zf.open('node-data.csv'), encoding='utf-8') as f:
                ret['node-data'] = pd.read_csv(f, sep='\t')

        return ret
