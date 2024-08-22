pubmed-dataset
---

# Overview
This repo provides two things:
1. A version of the Pubmed graph learning dataset ([Sen et al,
   2008](https://doi.org/10/ggn9hw)) rebuilt from scratch from the Pubmed API.
   Unlike the original version, this one includes the text of titles and
   abstracts, making it more suitable for research on models of text-attributed
   graphs (TAGs).
2. Scripts to do this rebuilding or generate similar TAGs for other sets of
   articles identified by PMIDs.

The new dataset is available at
[`src/pubmed/data/pubmed-new.zip`](https://github.com/mit-ccc/pubmed-dataset/blob/main/src/pubmed/data/pubmed-new.zip)
and can also be accessed in python:
```
import pubmed
dataset = pubmed.new_pubmed_dataset()
```

# Using the pull scripts
To pull the new dataset again (rather than use the cached version), you can use
the command line interface this package provides and run:
```
$ pubmed-pull --progress output
```

The output will be saved in three files, `graph.csv`, `texts.csv`, and
`node-data.csv`, under the `output` directory. (The `--progress` argument shows
a progress bar.)

To provide your own list of PMIDs, put them one per line in a file (no header):
```
$ cat my-pmids-list.txt
23582423
234897421
23582521
1823502
182024913
138240813
...

$ pubmed-pull --progress --infile my-pmids-list.txt output
```

Output will be in the same format as for the built-in Pubmed benchmark list.

# Citations
If you use this dataset or the pull scripts, please cite our paper:
```
@inproceedings{brannon-etal-2024-congrat,
    title = {{C}on{G}ra{T}: Self-Supervised Contrastive Pretraining for Joint Graph and Text Embeddings},
    author = {Brannon, William and Kang, Wonjune and Fulay, Suyash and Jiang, Hang and Roy, Brandon and Roy, Deb and Kabbara, Jad},

    booktitle = {Proceedings of TextGraphs-17: Graph-based Methods for Natural Language Processing},
    editor = {Ustalov, Dmitry and Gao, Yanjun and Panchenko, Alexander and Tutubalina, Elena and Nikishina, Irina and Ramesh, Arti and Sakhovskiy, Andrey and Usbeck, Ricardo and Penn, Gerald and Valentino, Marco},

    month = aug,
    year = {2024},
    address = {Bangkok, Thailand},
    publisher = {Association for Computational Linguistics},
    url = {https://aclanthology.org/2024.textgraphs-1.2},
    pages = {19--39},

    abstract = {Learning on text-attributed graphs (TAGs), in which nodes are associated with one or more texts, has been the subject of much recent work. However, most approaches tend to make strong assumptions about the downstream task of interest, are reliant on hand-labeled data, or fail to equally balance the importance of both text and graph representations. In this work, we propose Contrastive Graph-Text pretraining (ConGraT), a general, self-supervised approach for jointly learning separate representations of texts and nodes in a TAG. Our method trains a language model (LM) and a graph neural network (GNN) to align their representations in a common latent space using a batch-wise contrastive learning objective inspired by CLIP. We further propose an extension to the CLIP objective that leverages graph structure to incorporate information about inter-node similarity. Extensive experiments demonstrate that ConGraT outperforms baselines on various downstream tasks, including node and text category classification, link prediction, and language modeling. Finally, we present an application of our method to community detection in social graphs, which enables finding more textually grounded communities, rather than purely graph-based ones.},
}
```

The original Pubmed dataset:
```
@article{senCollectiveClassificationNetwork2008,
	title = {Collective {Classification} in {Network} {Data}},
	author = {Sen, Prithviraj and Namata, Galileo and Bilgic, Mustafa and Getoor, Lise and Galligher, Brian and Eliassi-Rad, Tina},

	journal = {AI Magazine},
	volume = {29},
	number = {3},
	pages = {93},
	year = {2008},
	month = sep,

	doi = {10/ggn9hw},
	url = {https://www.aaai.org/ojs/index.php/aimagazine/article/view/2157},

	abstract = {Many real-world applications produce networked data such as the world-wide web (hypertext documents connected via hyperlinks), social networks (for example, people connected by friendship links), communication networks (computers connected via communication links) and biological networks (for example, protein interaction networks). A recent focus in machine learning research has been to extend traditional machine learning classification techniques to classify nodes in such networks. In this article, we provide a brief introduction to this area of research and how it has progressed during the past decade. We introduce four of the most widely used inference algorithms for classifying networked data and empirically compare them on both synthetic and real-world data.},
}
```
