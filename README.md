# smict

This repository contains the code for the paper "A Simple Method for Inducing Class Taxonomies in Knowledge Graphs" by Marcin Pietrasik and Marek Reformat.

Citation:
```
@inproceedings{pietrasik2020simple,
  title={A Simple Method for Inducing Class Taxonomies in Knowledge Graphs},
  author={Pietrasik, Marcin and Reformat, Marek},
  booktitle={European Semantic Web Conference},
  pages={53--68},
  year={2020},
  organization={Springer}
}
```

## Installation

The code for our method uses the Python 3.6.6 standard library, no outside packages are required to be installed. Simply extract the dataset archives in the datasets directory and run `python smict.py`

To run the methods used for comparison in our paper, the following packages are required:
* networkx
* numpy
* sklearn

Having installed the required packages, run the code using `python heymann_garcia-molina.py` or `python schmitz.py`

## Runtime Instructions

smict.py takes two optional command line arguments:

| Parameter                 | Default       | Description   |	
| :------------------------ |:-------------:| :-------------|
| -d --dataset 	      |	dbpedia50000  | name of dataset in datasets directory on which subsumption axioms are generated
| -a --alpha          | 0.7           | value of alpha, the decay hyperparameter

heymann_garcia-molina.py takes two optional command line arguments:

| Parameter                 | Default       | Description   |	
| :------------------------ |:-------------:| :-------------|
| -d --dataset 	      |	dbpedia50000  | name of dataset in datasets directory on which subsumption axioms are generated
| -t --threshold      | 0.3           | value of the threshold hyperparameter

schmitz.py takes two optional command line arguments:

| Parameter                 | Default       | Description   |	
| :------------------------ |:-------------:| :-------------|
| -d --dataset 	      |	dbpedia50000  | name of dataset in datasets directory on which subsumption axioms are generated
| -t --threshold      | 0.8           | value of the threshold hyperparameter
