from argparse import ArgumentParser
from os import listdir, getcwd
from pathlib import Path
from random import shuffle

def main():

    #Initialize annotations and vocabulary
    annotations = {}
    vocabulary = []

    #Set decay factor, alpha, and dataset
    argument_parser = ArgumentParser(description='Generate subsumption axioms for document-tag pairs')
    argument_parser.add_argument('-d', '--dataset', help='Name of dataset in datasets directory', default = 'dbpedia50000')
    argument_parser.add_argument('-a', '--alpha', help='Float value of the alpha hyperparameter (default = 0.7)', default=0.7, type=float)
    arguments = argument_parser.parse_args()

    dataset = arguments.dataset
    alpha = arguments.alpha

    if alpha < 0.0 or alpha > 1:
        raise ValueError('Alpha value must be between 0 and 1 inclusive.')

    #Read in dataset into annotations and vocabulary
    for filename in listdir(getcwd() + '/datasets/' + dataset):
        with open(Path(getcwd() + '/datasets/' + dataset + '/'+ filename), encoding='utf-8') as input_file:
            lines = input_file.readlines()
            assert len(lines) == 1
            annotations[filename] = lines[0].lower().strip().split(" ")
            for tag in annotations[filename]:
                if tag not in vocabulary:
                    vocabulary.append(tag)
    shuffle(vocabulary)

    #Initialize and calulate the amount of documents annotated by each tag and tag pair
    D_counts = {}
    D_joint_counts = {}
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
                if (tag1, tag2) not in D_joint_counts:
                    D_joint_counts[(tag1, tag2)] = 1
                else:
                    D_joint_counts[(tag1, tag2)] += 1
                if (tag2, tag1) not in D_joint_counts:
                    D_joint_counts[(tag2, tag1)] = 1
                else:
                    D_joint_counts[(tag2, tag1)] += 1

    #Calculate generality for each tag and sort in descending order
    generality = []
    for tag1 in vocabulary:
        summer = 0
        for tag2 in vocabulary:
            if (tag1, tag2) in D_joint_counts:
                summer += D_joint_counts[(tag1, tag2)] / D_counts[tag2]
        generality.append((tag1, summer))
    generality.sort(key=lambda x: x[1], reverse = True) 

    #Initialize taxonomy with the tag with the highest generality
    root_node = generality.pop(0)[0]
    in_graph_children = { root_node: []}
    in_graph_path_up = {root_node : []}

    #Add tags to the taxonomy greedily in descending generality according to the higest similarity
    for entry in generality:
        child_tag = entry[0]
        highest_similarity = -1
        highest_similarity_tag = None

        for potential_parent_tag in in_graph_children:

            similarity = 0
            level = 0
            if (child_tag, potential_parent_tag) in D_joint_counts:
                similarity += (D_joint_counts[(child_tag, potential_parent_tag)] / D_counts[child_tag]) * (alpha ** level)
                level += 1
                
                for upstream_tag in in_graph_path_up[potential_parent_tag]:
                    if (upstream_tag, child_tag) in D_joint_counts:
                        similarity +=  (D_joint_counts[(child_tag, upstream_tag)] / D_counts[child_tag]) * (alpha ** level)
                    level += 1

            if similarity > highest_similarity:
                highest_similarity = similarity + 0
                highest_similarity_tag = potential_parent_tag

        in_graph_children[highest_similarity_tag].append(child_tag)
        in_graph_children[child_tag] = []

        in_graph_path_up[child_tag] = list([highest_similarity_tag]) + list(in_graph_path_up[highest_similarity_tag])

    #Write subsumption axioms to file
    with Path('smict_subsuptions_axioms_' + dataset).open('w', encoding="utf-8") as output_file:
        for node1 in in_graph_children:
            for node2 in in_graph_children[node1]:
                output_file.write(node1.lower() + " " +  node2.lower() + "\n")

if __name__ == '__main__':
    main()
