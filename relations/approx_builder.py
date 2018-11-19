# New builder class which makes use of our new data generation

import random
from collections import defaultdict
import itertools as it
from actors.actor import Actor
from utils.utils import pairwise
import copy
from actors.ancestry import Ancestry
from store.store import Store
import json
import pickle

store = Store()

class RelationBuilder:
    """
    Relation builder class

    Steps:
    - Accept a skeleton class
    - Iteratively:
        - Invert the relations
        - Sample edge e (n1, n2)
        - Select the rule which matches this edge e (n1,n2) -> r
        - introduce a variable x so that (n1,x) + (x,n2) -> r
        - find the x which satifies both s.t x =/= {n1, n2}
        - either add to story
        - or recurse
    """

    def __init__(self, anc, boundary=True):
        self.anc = anc
        self.rules = store.rules_store
        self.relations_obj = store.relations_store
        self.boundary = boundary
        # extract all possible relations from the store
        self.all_rel = set()
        for k,v in self.rules.items():
            self.all_rel.add(k)
            for c,p in v.items():
                self.all_rel.add(c)
                self.all_rel.add(p)
        # save the edges which are used already
        self.done_edges = set()


    def invert_rel(self):
        """
        Invert the relations
        :return:
        """
        inv_family = copy.deepcopy(self.anc.family)
        for edge, rel in self.anc.family.items():
            inv_rel = 'inv-' + rel
            if inv_rel in self.all_rel:
                inv_family[(edge[1], edge[0])] = inv_rel
        self.anc.family = inv_family

    def almost_complete(self,edge):
        """
        Build an almost complete graph by iteratively applying the rules
        Recursively apply rules and invert
        :return:
        """
        self.invert_rel()
        # left edges
        keys = list(self.anc.family.keys())
        edge_1 = [self.construct(e, edge) for e in keys if e[1] == edge[0]]
        edge_2 = [self.construct(edge, e) for e in keys if e[0] == edge[1]]
        edge_1 = list(filter(None.__ne__, edge_1))
        edge_2 = list(filter(None.__ne__, edge_2))
        for e in edge_1:
            self.almost_complete(e)
        for e in edge_2:
            self.almost_complete(e)



    def construct(self, edge_1, edge_2):
        # dont allow self edges
        if edge_1[0] == edge_1[1]:
            return None
        if edge_2[0] == edge_2[1]:
            return None
        if edge_1[1] == edge_2[0] and edge_1[0] != edge_2[1]:
            n_edge = (edge_1[0], edge_2[1])
            if n_edge not in self.anc.family and (edge_1 in self.anc.family and self.anc.family[edge_1] in self.rules):
                if edge_2 in self.anc.family and self.anc.family[edge_2] in self.rules[self.anc.family[edge_1]]:
                    n_rel = self.rules[self.anc.family[edge_1]][self.anc.family[edge_2]]
                    self.anc.family[n_edge] = n_rel
                    return n_edge
        return None



    def build(self, num_rel=2):
        available_edges = set([k for k, v in self.anc.family.items()]) - self.done_edges
        story = ''
        while(len(story) == 0):
            edge = random.choice(list(available_edges))
            story = self.derive(edge, [], k=num_rel-1)
            self._test_story(story)
            story = [self.stringify(s) for s in story]
            story = ''.join(story)
        target = self.stringify(edge)
        return (story, target)

    def derive(self, edge, ignore_edges, k=1):
        self.invert_rel()
        # for each node in graph, check if (edge[0],node) and (node, edge[1]) exists.
        found = False
        for node_id in self.anc.family_data.keys():
            var_l = (edge[0], node_id)
            var_r = (node_id, edge[1])
            if var_l == edge or var_r == edge or var_l in ignore_edges or var_r in ignore_edges:
                continue
            if var_l in self.anc.family and var_r in self.anc.family:
                found = [var_l, var_r]
                break
        one_step_story = [var_l, var_r]
        k = k - 1
        if found:
            if k==0:
                return one_step_story
            else:
                # we could expand the current variables either in left or right direction
                # but controlling for the depth in both directions is hard
                # so for now we would unroll only in left direction
                ignore_edges.append(edge)
                l_story = self.derive(var_l, ignore_edges, k)
                #ignore_edges.extend(l_story)
                #r_story = self.derive(var_r, ignore_edges, k)
                l_step_story = copy.copy(l_story)
                l_step_story.extend([var_r])
                #r_step_story = [var_l]
                #r_step_story.extend(r_story)
                #if len(l_story) == 0 and len(r_story) == 0:
                #    return one_step_story
                #elif len(l_story) == 0 and len(r_story) > 0:
                #    return l_step_story
                #elif len(r_story) == 0 and len(l_story) > 0:
                #    return r_step_story
                #else:
                #    return max(l_step_story, r_step_story, key=len)
                return l_step_story
        else:
            return []

    def stringify(self, edge):
        """
        Build story string from the edge
        :param edge: tuple
        :return:
        """
        # get node attributes
        node_a_attr = self.anc.family_data[edge[0]]
        node_b_attr = self.anc.family_data[edge[1]]
        relation = self.anc.family[edge]
        placeholders = self.relations_obj[relation][node_b_attr.gender]
        placeholder = random.choice(placeholders)
        node_a_name = node_a_attr.name
        node_b_name = node_b_attr.name
        assert node_a_name != node_b_name
        if self.boundary:
            node_a_name = '[{}]'.format(node_a_name)
            node_b_name = '[{}]'.format(node_b_name)
        text = placeholder.replace('e_1', node_a_name)
        text = text.replace('e_2', node_b_name)
        return text + '. '

    def _test_story(self, story):
        """
        Given a list of edges of the story, test whether they are logically valid
        (x,y),(y,z) is valid, (x,y),(x,z) is not
        :param story: list of tuples
        :return:
        """
        for e_i in range(len(story) - 1):
            assert story[e_i][-1] == story[e_i + 1][0]


if __name__=='__main__':
    anc = Ancestry(max_levels=2, min_child=2, max_child=2)
    anc.simulate()
    rb = RelationBuilder(anc)
    print(rb.anc.family)
    for i in range(len(anc.family_data)):
        for j in range(len(anc.family_data)):
            if i!=j:
                rb.almost_complete((i,j))
    print(rb.anc.family)
    pickle.dump(rb, open('rb.pkl','wb'))
    story, target = rb.build(num_rel=3)
    print(story)
    print(target)

