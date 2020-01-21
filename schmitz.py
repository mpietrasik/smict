from argparse import ArgumentParser
from os import listdir, getcwd
from random import shuffle
from pathlib import Path

def main():

    annotations = {}
    tag_vector = {}
    vocabulary = []

    #Set threshold and dataset
    argument_parser = ArgumentParser(description='Implementation of Schmitz method of inducing tag hierarchy')
    argument_parser.add_argument('-d', '--dataset', help='Name of dataset in datasets directory', default = 'dbpedia50000')
    argument_parser.add_argument('-t', '--threshold', help='Float value of the threshold hyperparameter (default = 0.8)', default=0.8, type=float)
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

    #Calculate D_counts and conditional counts
    D_counts = {}
    conditional_counts = {}
    for annotation in annotations:
        for tag in annotations[annotation]:
            if tag not in D_counts:
                D_counts[tag] = 1
            else:
                D_counts[tag] += 1
        for tag1 in annotations[annotation]:
            for tag2 in annotations[annotation]:
                if tag1 == tag2:
                    continue
                if (tag1,tag2) not in conditional_counts:
                    conditional_counts[(tag1,tag2)] = 1
                else:
                    conditional_counts[(tag1,tag2)] += 1

    #Generate potential subsumptions
    subsumptions = []
    for tag1 in vocabulary:
        for tag2 in vocabulary:
            if tag1 == tag2:
                continue
            if (tag1,tag2) not in conditional_counts:
                continue
            xIy = conditional_counts[(tag1,tag2)] / D_counts[tag2]
            yIx = conditional_counts[(tag2,tag1)] / D_counts[tag1]

            if xIy >= threshold and yIx < threshold and D_counts[tag1] > 0 and D_counts[tag2] > 0:
                subsumptions.append((tag1,tag2))    
    shuffle(subsumptions)

    #Find subsumptions to prune in order to make a tree
    remove_list = []
    for subsumption1 in subsumptions:
        parent1 = subsumption1[0]
        child1 = subsumption1[1]
        for subsumption2 in subsumptions:
            if subsumption1 != subsumption2:
                parent2 = subsumption2[0]
                child2 = subsumption2[1]
                if child1 == child2:
                    if (parent1, parent2) in subsumptions:
                        remove_list.append((parent1, child1))

    #Prune subsumptions to create a tree
    remove_list = list(set(remove_list))
    for rmv in remove_list:
        subsumptions.remove(rmv)

    #Find parent for each tag
    final_relations = []
    for tag in vocabulary:
        tag_parents = []
        for subsumption in subsumptions:
            if subsumption[1] == tag:
                tag_parents.append(subsumption[0])
        if len(tag_parents) > 1:
            max_weight = -1
            parent = None
            for possible_parent in tag_parents:
                possible_parent_weight = 0
                for annotation in annotations:
                    if tag in annotations[annotation] and possible_parent in annotations[annotation]:
                        possible_parent_weight += 1
                if possible_parent_weight > max_weight:
                    max_weight = possible_parent_weight
                    parent = possible_parent
        elif len(tag_parents) == 0:
            continue
        else:
            final_relations.append((tag_parents[0], tag))
    
    #Write subsumption axioms to file
    with Path('schmitz_subsuptions_axioms_' + dataset).open('w', encoding="utf-8") as output_file:
        for relation in final_relations:
            output_file.write(relation[0].lower() + " " +  relation[1].lower() + "\n")

if __name__ == '__main__':
    main()