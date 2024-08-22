import os
import logging
import xml.etree.ElementTree as et

import requests as rq


logger = logging.getLogger(__name__)


class Entry:
    # 1) see https://www.ncbi.nlm.nih.gov/pmc/tools/get-metadata/
    # 2) see also https://www.ncbi.nlm.nih.gov/pmc/tools/cites-citedby/, but
    #    the efetch endpoint seems to have the PMIDs of cited articles already
    # 3) see https://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html
    #    for an English description of this XML schema + the DTD
    # 4) no authentication needed, thanks NIH

    # pylint: disable-next=line-too-long
    _base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id='

    def __init__(self, pmid, cache_dir=None):
        super().__init__()

        if isinstance(pmid, str):
            pmid = int(pmid)

        self.data = {'node_id': pmid}
        self.texts, self.references = [], []
        self.api_response = None
        self.cache_dir = cache_dir

        self.is_populated = False

    @property
    def pmid(self):
        return self.data['node_id']

    @property
    def cache_path(self):
        if self.cache_dir is not None:
            return os.path.join(self.cache_dir, str(self.pmid) + '.xml')

        return None

    @property
    def is_cached(self):
        return self.cache_path is not None and os.path.exists(self.cache_path)

    def ensure_api_response(self):
        # Use the cached version if we have it
        if self.is_cached:
            with open(self.cache_path, 'rt', encoding='utf-8') as f:
                self.api_response = f.read().strip()

            return self

        # Get it if we don't
        resp = rq.get(self._base_url + str(self.pmid), timeout=30)
        self.api_response = resp.text

        # Cache it if we got it
        if self.cache_path is not None:
            with open(self.cache_path, 'wt', encoding='utf-8') as f:
                f.write(self.api_response.strip())

        return self

    def populate(self):
        self.ensure_api_response()

        root = et.fromstring(self.api_response)
        assert root.tag == 'PubmedArticleSet'
        assert len(root) == 1

        obj = root[0]
        assert len(obj) == 2
        assert {c.tag for c in obj} == {'MedlineCitation', 'PubmedData'}

        citation = obj.find('MedlineCitation')
        assert int(citation.find('PMID').text) == self.pmid

        article = citation.find('Article')
        journal = article.find('Journal')
        abstract = article.find('Abstract')

        date = article.find('ArticleDate')
        if date is None:
            date = citation.find('DateCompleted')

        pubmed_data = obj.find('PubmedData')
        assert 'PublicationStatus' in [n.tag for n in pubmed_data]
        assert 'ArticleIdList' in [n.tag for n in pubmed_data]

        ## Texts
        self.texts += [{
            'kind': 'title',
            'order': 0,
            'content': article.find('ArticleTitle').text,
        }]

        for i, para in enumerate(abstract):
            if 'Label' in para.attrib.keys():
                txt = para.attrib['Label'] + '\n'
            else:
                txt = ''

            txt += para.text if para.text is not None else ''

            self.texts += [{
                'kind': 'abstract',
                'order': i,
                'content': txt,
            }]

        ## Article data
        self.data['publication_status'] = pubmed_data.find('PublicationStatus').text

        try:
            self.data['journal_issn'] = journal.find('ISSN').text
        except AttributeError:  # NoneType has no attribute 'text'
            self.data['journal_issn'] = None

        try:
            self.data['journal_name'] = journal.find('Title').text
        except AttributeError:  # NoneType has no attribute 'text'
            self.data['journal_name'] = None

        self.data['date'] = '-'.join([
            date.find('Year').text,
            date.find('Month').text,
            date.find('Day').text,
        ])

        for aid in pubmed_data.find('ArticleIdList'):
            id_type = aid.attrib['IdType']
            self.data['article_id_' + id_type] = aid.text

        # these are "MeSH publication types", see
        # https://www.nlm.nih.gov/mesh/2019/download/NewPubTypes2019.pdf
        # for what the alphanumeric codes mean
        for ptl in article.find('PublicationTypeList'):
            col = 'publication_type_' + ptl.attrib['UI']
            self.data[col] = True

        ## References
        refs = pubmed_data.find('ReferenceList')
        if refs is not None:
            for ref in refs:
                ids = ref.find('ArticleIdList')
                if ids is None:
                    continue

                for ent in ids:
                    if ent.attrib['IdType'] == 'pubmed':
                        self.references += [int(ent.text)]
                        continue

        self.is_populated = True

        return self
