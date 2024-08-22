import os

import time
import random
import logging

import pandas as pd

from tqdm import tqdm

from .entry import Entry


logger = logging.getLogger(__name__)


class EntrySet:
    def __init__(self, pmids, cache_dir=None, progress=False):
        super().__init__()

        self.pmids = pmids
        self.cache_dir = cache_dir
        self.progress = progress

        self.entries = [
            Entry(pmid, cache_dir=cache_dir)
            for pmid in self.pmids
        ]

        if cache_dir is not None:
            os.makedirs(cache_dir, exist_ok=True)

    @property
    def is_populated(self):
        return all(e.is_populated for e in self.entries)

    def populate(self):
        for ent in tqdm(self.entries, disable=(not self.progress)):
            if not ent.is_populated:
                if not ent.is_cached:
                    # let's not get rate limited or banned or something
                    if random.random() < 0.05:
                        sleep_time = 6 + random.gauss(0, 1)
                    else:
                        sleep_time = 2 * random.random()
                    logger.debug('Sleeping %s seconds', sleep_time)
                    time.sleep(sleep_time)

                logger.info('Populating %s', ent.pmid)

                try:
                    ent.populate()
                except Exception:  # pylint: disable=broad-except
                    logger.exception('Error on populating %s', ent.pmid)

        return self

    def to_pandas(self):
        assert self.is_populated

        # Node data
        node_data = [e.data for e in self.entries]
        node_data = pd.DataFrame.from_dict(node_data, orient='columns')
        for col in node_data.columns:
            if col.startswith('publication_type_'):
                node_data[col] = node_data[col].fillna(False)

            if node_data[col].dtype.name == 'bool':
                node_data[col] = node_data[col].astype(int)

        # Node texts
        texts = pd.DataFrame.from_dict([
            {'node_id': ent.pmid, **text}
            for ent in self.entries
            for text in ent.texts
        ], orient='columns')

        # Graph edges
        graph = pd.DataFrame.from_dict([
            {'source': ent.pmid, 'target': tgt}
            for ent in self.entries
            for tgt in ent.references
        ], orient='columns')

        # Filter
        graph = graph.loc[graph['source'].isin(node_data['node_id']), :]
        graph = graph.loc[graph['target'].isin(node_data['node_id']), :]

        return {
            'graph': graph,
            'texts': texts,
            'node-data': node_data,
        }
