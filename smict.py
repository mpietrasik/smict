import time
import os
import rdflib
import json
import random
from pathlib import Path
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import os
from collections import OrderedDict
from sklearn import metrics
import numpy as np
import networkx as nx
import operator
import random

timer = time.time()

annotations = {}
tag_vector = {}
vocabulary = []

alpha = 0.8
#dataset = 'random_hard100000_organisms'
dataset = 'dbpedia_random_hard100000_location_removed'

timer = time.time()

for filename in os.listdir(os.getcwd() + '/../datasets/regular/' + dataset):
    with open(Path(os.getcwd() + '/../datasets/regular/'+ dataset + '/'+ filename), encoding='utf-8') as input_file:
        lines = input_file.readlines()
        assert len(lines) == 1

        annotations[filename] = lines[0].lower().strip().split(" ")
        for tag in annotations[filename]:
            if tag not in vocabulary:
                vocabulary.append(tag)

subsumptions = []

random.shuffle(vocabulary)

print('I/O + shuffle', time.time() - timer)
timer = time.time()

D_counts = {}
joint_counts = {}

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
            if (tag1,tag2) not in joint_counts:
                joint_counts[(tag1,tag2)] = 1
            else:
                joint_counts[(tag1,tag2)] += 1

            if (tag2, tag1) not in joint_counts:
                joint_counts[(tag2,tag1)] = 1
            else:
                joint_counts[(tag2,tag1)] += 1

print('Metrics', time.time() - timer)
timer = time.time()

generality = []
for x in vocabulary:
    summer = 0
    counter = 0
    for y in vocabulary:
        if (x,y) in joint_counts:
            summer += joint_counts[(x,y)] / D_counts[y]
        counter += 1
    generality.append((x, summer / counter))

print('Generality', time.time() - timer)
timer = time.time()
generality.sort(key=lambda x: x[1], reverse = True) 
print('Generality sort', time.time() - timer)
timer = time.time()

root_node = generality.pop(0)[0]
in_graph_children = { root_node: []}
in_graph_path_up = {root_node : []}

'''
for x in vocabulary:
    for y in vocabulary:
        if x != y:
            if joint_counts[(x,y)] != joint_counts[y,x]:
                print(joint_counts[(x,y)], joint_counts[(y,x)])
                assert joint_counts[(x,y)] == joint_counts[y,x]
'''

cc = 0
for entry in generality:
    child_tag = entry[0]
    cc += 1
    highest_similarity = -1
    highest_similarity_tag = None

    for potential_parent_tag in in_graph_children:

        similarity = 0
        #similarity_sum = 0
        printlist = []
        '''
        similarity_list = []
        weights1 = list(np.geomspace(0.9,0.1, len(in_graph_path_up[potential_parent_tag]) + 1)) #* (len(in_graph_path_up[potential_parent_tag]) + 1)
        weights1 = [0] * (len(in_graph_path_up[potential_parent_tag]) + 1)
        weights1[0] = 1
        '''
        #print('\n\n\n\n')

        #decay = 1
        #alpha = 0.8
        counter = 0
        if (child_tag, potential_parent_tag) in joint_counts:
            
            #similarity = (joint_counts[(child_tag, potential_parent_tag)] / D_counts[child_tag] ) * (len(in_graph_path_up[potential_parent_tag]) / (len(in_graph_path_up[potential_parent_tag]) +1) )
            
            
            similarity += (joint_counts[(child_tag, potential_parent_tag)] / D_counts[child_tag]) * (alpha ** counter)#(1 / decay)
            #similarity_list.append(joint_counts[(child_tag, potential_parent_tag)] / D_counts[child_tag])
            #printlist.append(''.join([i for i in potential_parent_tag if not i.isdigit()]))
            #printlist.append(joint_counts[(child_tag, potential_parent_tag)] / D_counts[child_tag])
            #decay += 1.8
            counter += 1
            
            for upstream_tag in in_graph_path_up[potential_parent_tag]:
                if (upstream_tag, child_tag) in joint_counts:
                    similarity +=  (joint_counts[(child_tag, upstream_tag)] / D_counts[child_tag]) * (alpha ** counter)#(1 / decay)
                    #similarity_list.append(joint_counts[(child_tag, upstream_tag)] / D_counts[child_tag])
                    #printlist.append(''.join([i for i in upstream_tag if not i.isdigit()]))
                    #printlist.append(joint_counts[(child_tag, upstream_tag)] / D_counts[child_tag])
                #else:
                #    similarity_list.append(0)
                #decay += 1.8
                counter += 1
            
            #assert len(similarity_list) == len(weights1)  

            #print(child_tag, potential_parent_tag)
            #print(len(similarity), len(weights1))
            
            
        #else:
        #    similarity_list = [0] * (len(in_graph_path_up[potential_parent_tag]) + 1)
        #print('joint', joint_counts[(child_tag, potential_parent_tag)],  D_counts[child_tag], joint_counts[(child_tag, potential_parent_tag)] / D_counts[child_tag])
        #print('similarity list raw', similarity_list)
        
        #similarity = np.average(similarity_list, weights = weights1)
        #similarity = similarity_sum + 0

        if similarity > highest_similarity:
            highest_similarity = similarity + 0
            highest_similarity_tag = potential_parent_tag
    #print()
    in_graph_children[highest_similarity_tag].append(child_tag)
    in_graph_children[child_tag] = []

    in_graph_path_up[child_tag] = list([highest_similarity_tag]) + list(in_graph_path_up[highest_similarity_tag])

    #print(in_graph_children)
    #print(in_graph_path_up)
    '''
    if cc > 50:
        for node1 in in_graph_children:
            for node2 in in_graph_children[node1]:
                print(node1.lower(), node2.lower())
        quit()
    '''
'''
for node1 in in_graph_children:
    for node2 in in_graph_children[node1]:
        print(node1.lower(), node2.lower())
'''
print('Adding to graph', time.time() - timer)
timer = time.time()

#with Path('../results/our_model_' + dataset + "_" + str(random.randint(1,1000000000))).open('w', encoding="utf-8") as output_file:
with Path('../results/our_model_' + dataset).open('w', encoding="utf-8") as output_file:
    for node1 in in_graph_children:
        for node2 in in_graph_children[node1]:
            output_file.write(node1.lower() + " " +  node2.lower() + "\n")

#print('qweqwe',in_graph_path_up['gymnast'])
#print('qweqwe2',in_graph_path_up['model'])


#print(conditional_counts[('railwayline','publictransitsystem')] / D_counts['publictransitsystem'])
#print(conditional_counts[('publictransitsystem','railwayline')] / D_counts['railwayline'])
#print(conditional_counts[('publictransitsystem','company')] / D_counts['company'])
#print(conditional_counts[('company','publictransitsystem')] / D_counts['publictransitsystem'])
quit()
print()
print(conditional_counts[('bodybuilder','gymnast')] / D_counts['gymnast'])
print(conditional_counts[('athlete','gymnast')] / D_counts['gymnast'])
print(conditional_counts[('person','gymnast')] / D_counts['gymnast'])
print(conditional_counts[('agent','gymnast')] / D_counts['gymnast'])
print()
print((conditional_counts[('gymnast','bodybuilder')] / D_counts['bodybuilder'])  * (conditional_counts[('bodybuilder','gymnast')] / D_counts['gymnast']) )
print( (   conditional_counts[('gymnast','athlete')] / D_counts['athlete']  ) * (    conditional_counts[('athlete','gymnast')] / D_counts['gymnast']       ))
print( (   conditional_counts[('gymnast','person')] / D_counts['person']  ) * (   conditional_counts[('person','gymnast')] / D_counts['gymnast']        ))
print( (  conditional_counts[('gymnast','agent')] / D_counts['agent']   ) * (  conditional_counts[('agent','gymnast')] / D_counts['gymnast']         ))

quit()

print(conditional_counts[('model','bodybuilder')] / D_counts['bodybuilder'])
#print(conditional_counts[('model','athlete')] / D_counts['athlete'])
print(conditional_counts[('model','person')] / D_counts['person'])


quit()
print(conditional_counts[('mountainpass','naturalplace')] / D_counts['naturalplace'])
print(conditional_counts[('naturalplace','mountainpass')] / D_counts['mountainpass'])

print(conditional_counts[('populatedplace','location')] / D_counts['location'])
print(conditional_counts[('location','populatedplace')] / D_counts['populatedplace'])



