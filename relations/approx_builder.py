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

    Changes:
        - Relation types are "family","work", etc (as given in ``relation_types``
        - When applying the rules, make sure to confirm to these types
    """

    def __init__(self, anc, boundary=True):
        self.anc = anc
        self.rules = store.rules_store
        self.comp_rules = self.rules['compositional']
        self.inv_rules = self.rules['inverse-equivalence']
        self.sym_rules = self.rules['symmetric']
        self.eq_rules = self.rules['equivalence']
        self.relation_types = self.rules['relation_types']
        self.relations_obj = store.relations_store
        self.boundary = boundary
        # save the edges which are used already
        self.done_edges = set()


    def invert_rel(self, rel_type='family'):
        """
        Invert the relations
        :return:
        """
        if rel_type not in self.inv_rules:
            return None
        inv_family = copy.deepcopy(self.anc.family)
        for edge, rel in self.anc.family.items():
            relation = rel[rel_type]
            if relation in self.inv_rules[rel_type]:
                inv_rel = self.inv_rules[rel_type][relation]
                if (edge[1], edge[0]) not in inv_family:
                    inv_family[(edge[1], edge[0])] = {}
                inv_family[(edge[1], edge[0])][rel_type] = inv_rel
        self.anc.family = inv_family

    def equivalence_rel(self, rel_type='family'):
        """
        Use equivalence relations
        :return:
        """
        if rel_type not in self.eq_rules:
            return None
        n_family = copy.deepcopy(self.anc.family)
        for edge, rel in self.anc.family.items():
            relation = rel[rel_type]
            if relation in self.eq_rules[rel_type]:
                eq_rel = self.eq_rules[rel_type][relation]
                n_family[(edge[0],edge[1])][rel_type] = eq_rel

    def symmetry_rel(self, rel_type='family'):
        """
        Use equivalence relations
        :return:
        """
        if rel_type not in self.sym_rules:
            return None
        n_family = copy.deepcopy(self.anc.family)
        for edge, rel in self.anc.family.items():
            relation = rel[rel_type]
            if relation in self.sym_rules[rel_type]:
                sym_rel = self.sym_rules[rel_type][relation]
                if (edge[1], edge[0]) not in n_family:
                    n_family[(edge[1], edge[0])] = {}
                n_family[(edge[1], edge[0])][rel_type] = sym_rel


    def compose_rel(self, edge_1, edge_2, rel_type='family'):
        """
        Given an edge pair, add the edges into a single edge following the rules
        in the dictionary
        :param edge_1: (x,z)
        :param edge_2: (z,y)
        :param rel_type:
        :return: (x,y)
        """
        # dont allow self edges
        if edge_1[0] == edge_1[1]:
            return None
        if edge_2[0] == edge_2[1]:
            return None
        if edge_1[1] == edge_2[0] and edge_1[0] != edge_2[1]:
            n_edge = (edge_1[0], edge_2[1])
            if n_edge not in self.anc.family and \
                    (edge_1 in self.anc.family and
                     self.anc.family[edge_1][rel_type] in self.comp_rules[rel_type]):
                if edge_2 in self.anc.family and \
                        self.anc.family[edge_2][rel_type] in self.comp_rules[rel_type][self.anc.family[edge_1][rel_type]]:
                    n_rel = self.comp_rules[rel_type][self.anc.family[edge_1][rel_type]][self.anc.family[edge_2][rel_type]]
                    if n_edge not in self.anc.family:
                        self.anc.family[n_edge] = {}
                    self.anc.family[n_edge][rel_type] = n_rel
                    print(edge_1, edge_2, n_rel)
                    return n_edge
        return None

    def almost_complete(self,edge):
        """
        Build an almost complete graph by iteratively applying the rules
        Recursively apply rules and invert
        :return:
        """
        # apply symmetric, equivalence and inverse rules
        self.invert_rel()
        self.equivalence_rel()
        self.symmetry_rel()
        # apply compositional rules
        keys = list(self.anc.family.keys())
        edge_1 = [self.compose_rel(e, edge) for e in keys if e[1] == edge[0]]
        edge_2 = [self.compose_rel(edge, e) for e in keys if e[0] == edge[1]]
        edge_1 = list(filter(None.__ne__, edge_1))
        edge_2 = list(filter(None.__ne__, edge_2))
        for e in edge_1:
            self.almost_complete(e)
        for e in edge_2:
            self.almost_complete(e)

    def build(self, num_rel=2, fact_type=0):
        """
        Build the story and target. Select an edge from the graph and `derive` the story from
        the given edge.
        :param num_rel:
        :param fact_type: Choose the type of story to build.
            - 0 : Only provide the required relevant facts
            - 1 : Provide supporting facts. After creating the essential fact graph, expand on any
            k number of edges (randomly)
            - 2: Irrelevant facts: after creating the relevant fact graph, expand on an edge,
             but only provide dangling expansions
            - 3: Disconnected facts: along with relevant facts, provide a tree which is completely
            disconnected
        :return:
        """
        available_edges = set([k for k, v in self.anc.family.items()]) - self.done_edges
        story = ''
        while(len(story) == 0):
            edge = random.choice(list(available_edges))
            story = self.derive(edge, [], k=num_rel-1)
            self._test_story(story)
            assert story[0][0] == edge[0]
            assert story[-1][-1] == edge[-1]
            print('story', story)
            if len(story) <= 0:
                continue
            ignore_edges = copy.copy(story)
            ignore_edges.append(edge)
            if fact_type == 1:
                num_edges = random.choice(range(1, len(story)))
                sampled_edges = random.sample(story, num_edges)
                extra_story = []
                for se in sampled_edges:
                    ignore_edges.extend(extra_story)
                    extra_story.extend(self.derive(se, ignore_edges=ignore_edges, k=1))
                story.extend(extra_story)
            elif fact_type == 2:
                num_edges = random.choice(range(1, len(story)))
                sampled_edge = random.choice(story)
                extra_story = []
                for i in range(num_edges):
                    ignore_edges.extend(extra_story)
                    pair = self.derive(sampled_edge, ignore_edges=ignore_edges, k=1)
                    extra_story.append(pair[0])
                    sampled_edge = pair[0]
                story.extend(extra_story)
            elif fact_type == 3:
                nodes_story = set([y for x in list(story) for y in x])
                nodes_not_in_story = set(self.anc.family_data.keys()) - nodes_story
                possible_edges = [(x,y) for x,y in it.combinations(list(nodes_not_in_story), 2) if (x,y) in self.anc.family]
                num_edges = random.choice(range(1, len(possible_edges)))
                possible_edges = random.sample(possible_edges, num_edges)
                story.extend(possible_edges)
        print('final story', story)
        story = [self.stringify(s) for s in story]
        story = ''.join(story)
        print(edge)
        target = self.stringify(edge)
        return (story, target)

    def derive(self, edge, ignore_edges, k=1):
        """
        Given an edge, break the edge into two compositional edges from the given
        family graph. Eg, if input is (x,y), break the edge into (x,z) and (z,y)
        :param edge: Edge to break
        :param ignore_edges: Edges to ignore while breaking an edge. Used to ignore loops
        :param k: if k == 0, stop recursing
        :return:
        """
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
                print(edge, (var_l, var_r))
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
                l_step_story = copy.copy(l_story)
                l_step_story.extend([var_r])
                return l_step_story
        else:
            return [edge]

    def stringify(self, edge, rel_type='family'):
        """
        Build story string from the edge
        :param edge: tuple
        :return:
        """
        # get node attributes
        node_a_attr = self.anc.family_data[edge[0]]
        node_b_attr = self.anc.family_data[edge[1]]
        relation = self.anc.family[edge][rel_type]
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
    story, target = rb.build(num_rel=3, fact_type=3)
    print(story)
    print(target)

