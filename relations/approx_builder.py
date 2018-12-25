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
import uuid

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
        self.comp_rules_inv = self._invert_rule(self.rules['compositional'])
        self.inv_rules_inv = self._invert_rule(self.rules['inverse-equivalence'])
        self.sym_rules_inv = self._invert_rule(self.rules['symmetric'])
        self.eq_rules_inv = self._invert_rule(self.rules['equivalence'])
        self.relations_obj = store.relations_store
        self.boundary = boundary
        self.puzzles = {}
        self.puzzle_ct = 0
        # save the edges which are used already
        self.done_edges = set()

    def _invert_rule(self, rule):
        """
        Given a rule, invert it to be RHS:LHS
        :param rule:
        :return:
        """
        inv_rules = {}
        for tp, rules in rule.items():
            inv_rules[tp] = {}
            for key, val in rules.items():
                if type(val) == str:
                    if val not in inv_rules[tp]:
                        inv_rules[tp][val] = []
                    inv_rules[tp][val].append(key)
                else:
                    for k2, v2 in val.items():
                        if v2 not in inv_rules[tp]:
                            inv_rules[tp][v2] = []
                        inv_rules[tp][v2].append((key, k2))
        return inv_rules

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
        self.anc.family = n_family

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
        self.anc.family = n_family


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

    def build(self, num_rel=2):
        """
        Build the stories and targets for the current family configuration
        and save it in memory. These will be used later for post-processing
        :param num_rel:
        :return:
        """
        available_edges = set([k for k, v in self.anc.family.items()]) - self.done_edges
        for edge in available_edges:
            story, proof_trace = self.derive([edge], k=num_rel-1)
            if len(story) == num_rel:
                self.puzzles[self.puzzle_ct] = {
                    'edge': edge,
                    'story': story,
                    'proof': proof_trace
                }
                self.puzzle_ct += 1

    def add_facts(self, fact_id=1):
        """
        :param fact_id :
            For each stored puzzle, add different types of facts
                - 1 : Provide supporting facts. After creating the essential fact graph, expand on any
                k number of edges (randomly)
                - 2: Irrelevant facts: after creating the relevant fact graph, expand on an edge,
                 but only provide dangling expansions
                - 3: Disconnected facts: along with relevant facts, provide a tree which is completely
                separate from the proof path
        :return:
        """
        for puzzle_id, puzzle in self.puzzles.items():
            if fact_id == 1:
                # Supporting facts
                story = puzzle['story']
                extra_story = []
                for se in story:
                    e = self.expand(se)
                    if e:
                        if puzzle['edge'] not in e and len(set(e).intersection(set(story))) == 0 and len(set(e).intersection(set(extra_story))) == 0:
                            extra_story.extend(e)
                self.puzzles[puzzle_id]['fact_1'] = extra_story
            elif fact_id == 2:
                # Irrelevant facts
                num_edges = len(story)
                sampled_edge = random.choice(story)
                extra_story = []
                for i in range(num_edges):
                    tmp = sampled_edge
                    pair = self.expand(sampled_edge)
                    if pair:
                        for e in pair:
                            if e != puzzle['edge']:
                                extra_story.append(e)
                                sampled_edge = e
                    if tmp == sampled_edge:
                        sampled_edge = random.choice(story)
                self.puzzles[puzzle_id]['fact_2'] = extra_story
            elif fact_id == 3:
                # Disconnected facts
                nodes_story = set([y for x in list(story) for y in x])
                nodes_not_in_story = set(self.anc.family_data.keys()) - nodes_story
                possible_edges = [(x,y) for x,y in it.combinations(list(nodes_not_in_story), 2) if (x,y) in self.anc.family]
                num_edges = random.choice(range(1, len(possible_edges)))
                possible_edges = random.sample(possible_edges, num_edges)
                self.puzzles[puzzle_id]['fact_3'] = possible_edges
            else:
                raise NotImplementedError("Fact option {} not implemented".format(fact_id))

    def expand(self, edge, tp='family'):
        """
        Given an edge, break the edge into two compositional edges from the given
        family graph. Eg, if input is (x,y), break the edge into (x,z) and (z,y)
        following the rules
        :param edge: Edge to break
        :param ignore_edges: Edges to ignore while breaking an edge. Used to ignore loops
        :param k: if k == 0, stop recursing
        :return:
        """
        relation = self.anc.family[edge][tp]
        if relation not in self.comp_rules_inv[tp]:
            return None
        rules = list(self.comp_rules_inv[tp][relation])
        while len(rules) > 0:
            rule = random.choice(rules)
            rules.remove(rule)
            for node in self.anc.family_data.keys():
                e1 = (edge[0], node)
                e2 = (node, edge[1])
                if e1 in self.anc.family and self.anc.family[e1][tp] == rule[0] \
                        and e2 in self.anc.family and self.anc.family[e2][tp] == rule[1]:
                    return [e1, e2]
        return None

    def derive(self, edge_list, k=3):
        """
        Given a list of edges, expand elements from the edge until we reach k
        :param edge_list:
        :param k:
        :return:
        """
        proof_trace = []
        seen = set()
        while k>0:
            if len(set(edge_list)) - len(seen) == 0:
                break
            e = random.choice(list(set(edge_list) - seen))
            seen.add(e)
            ex_e = self.expand(e)
            if ex_e and (ex_e[0] not in seen and ex_e[1] not in seen and ex_e[0][::-1] not in seen and ex_e[1][::-1] not in seen):
                pos = edge_list.index(e)
                edge_list.insert(pos, ex_e[-1])
                edge_list.insert(pos, ex_e[0])
                edge_list.remove(e)
                #edge_list.extend(ex_e)
                proof_trace.append({e:ex_e})
                k = k-1
        return edge_list, proof_trace

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

    def generate_puzzles(self, extra_keys=[]):
        """
        Given stored puzzles, run `stringify` over them
        :param: extra_keys : this should contain the extra fact keys we want to add in the puzzles. We already generated
        the extra facts using `add_facts`, we just need to stringify them.
        :return:
        """
        puzzle_ids = self.puzzles.keys()
        for pi in puzzle_ids:
            self.puzzles[pi]['text_story'] = ''.join([self.stringify(e) for e in self.puzzles[pi]['story']])
            self.puzzles[pi]['text_target'] = self.stringify(self.puzzles[pi]['edge'])
            for key in extra_keys:
                self.puzzles[pi]['text_{}'.format(key)] = ''.join([self.stringify(e) for e in self.puzzles[pi][key]])

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
    anc = Ancestry(max_levels=3, min_child=2, max_child=2)
    anc.simulate()
    rb = RelationBuilder(anc)
    print(rb.anc.family)
    for i in range(len(anc.family_data)):
        for j in range(len(anc.family_data)):
            if i!=j:
                rb.almost_complete((i,j))
    print(rb.anc.family)
    rb.build(num_rel=3)
    rb.add_facts(fact_id=1)
    rb.generate_puzzles()
    print("Generated {} puzzles".format(len(rb.puzzles)))
    pickle.dump(rb, open('rb.pkl', 'wb'))

