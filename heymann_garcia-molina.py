from argparse import ArgumentParser
from networkx import Graph, closeness_centrality
from numpy import array
from os import listdir, getcwd
from pathlib import Path
from random import shuffle
from sklearn import metrics

def main():

    #Initialize containers
    annotations = {}
    tag_vector = {}
    vocabulary = []

    #Set threshold and dataset
    argument_parser = ArgumentParser(description='Implementation of Heymann and Garcia-Molina method of inducing tag hierarchy')
    argument_parser.add_argument('-d', '--dataset', help='Name of dataset in datasets directory', default = 'dbpedia50000')
    argument_parser.add_argument('-t', '--threshold', help='Float value of the threshold hyperparameter (default = 0.3)', default=0.3, type=float)
    arguments = argument_parser.parse_args()

    dataset = arguments.dataset
    threshold = arguments.threshold

    if threshold < 0.0 or threshold > 1:
        raise ValueError('Threshold value must be between 0 and 1 inclusive.')

    #Read in dataset into annotations and vocabulary
    for filename in listdir(getcwd() + '/datasets/' + dataset):
        with open(Path(getcwd() + '/datasets/' + dataset + '/'+ filename), encoding='utf-8') as input_file:
            lines = input_file.readlines()
            assert len(lines) == 1
            annotations[filename] = lines[0].strip().split(" ")
            for tag in annotations[filename]:
                if tag not in vocabulary:
                    vocabulary.append(tag)
    entities = list(annotations.keys())
    shuffle(vocabulary)

    #Calculate tag vectors and reshape them for faster cosine similarity computation
    for tag in vocabulary:
        tag_vector[tag] = [0] * len(entities)
        for entity in annotations:
            if tag in annotations[entity]:
                tag_vector[tag][entities.index(entity)] += 1

        assert sum(tag_vector[tag]) > 0

    tag_vector_reshaped = {}
    for tag1 in tag_vector:
        tag_vector_reshaped[tag1] = array(tag_vector[tag1]).reshape(1,-1)
        
    #Calcualte cosine similarities between tags
    similarities = {}
    i = 0
    for tag1 in tag_vector:
        j = 0
        for tag2 in tag_vector:
            if tag1 != tag2:
                if i < j:
                    cos = metrics.pairwise.cosine_similarity(tag_vector_reshaped[tag1], tag_vector_reshaped[tag2])[0][0]
                    similarities[(tag1, tag2)] = cos
                    similarities[(tag2, tag1)] = cos
            j += 1
        i += 1

    #Create similarity graph based on similarities above the threshold hyperparameter and calculate closeness centrality for each tag
    G = Graph()
    G.add_nodes_from(vocabulary)
    for pair in similarities:
        if similarities[pair] > threshold:
            G.add_edge(pair[0], pair[1])
    generality = []
    closeness_centrality_dict = closeness_centrality(G)

    #Sort tags based on generality as approximated by the closeness centrality
    for entry in closeness_centrality_dict:
        generality.append((entry, closeness_centrality_dict[entry]))
    generality.sort(key=lambda x: x[1], reverse = True) 

    #Perform greedy algorithm to add tags to hierarchy
    in_graph = {generality.pop(0)[0] : []}
    for entry in generality:
        tag1 = entry[0]

        highest_similarity = -1
        highest_similarity_tag = None

        for tag2 in in_graph:
            similarity =  similarities[(tag1, tag2)]
            if similarity > highest_similarity:
                highest_similarity = similarity + 0
                highest_similarity_tag = tag2

        in_graph[highest_similarity_tag].append(tag1)
        in_graph[tag1] = []

    #Write subsumption axioms to file
    with Path('heymann_garcia-molina_subsuptions_axioms_' + dataset).open('w', encoding="utf-8") as output_file:
        for node1 in in_graph:
            for node2 in in_graph[node1]:
                output_file.write(node1.lower() + " " +  node2.lower() + "\n")

if __name__ == '__main__':
    main()