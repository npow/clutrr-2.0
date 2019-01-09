# New builder class which makes use of our new data generation

import random
import itertools as it
import copy
from clutrr.store.store import Store
import uuid


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

    def __init__(self,args, store:Store, anc):
        self.anc = anc
        self.args = args
        self.rules = store.rules_store
        self.store = store
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
        self.boundary = args.boundary
        self.num_rel = args.relation_length
        self.puzzles = {}
        self.puzzle_ct = 0
        # save the edges which are used already
        self.done_edges = set()
        self.apply_almost_complete()

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


    def compose_rel(self, edge_1, edge_2, rel_type='family', verbose=False):
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
                    if verbose:
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

    def apply_almost_complete(self):
        """
        For each edge apply ``almost_complete``
        :return:
        """
        for i in range(len(self.anc.family_data)):
            for j in range(len(self.anc.family_data)):
                if i != j:
                    self.almost_complete((i, j))

    def build(self):
        """
        Build the stories and targets for the current family configuration
        and save it in memory. These will be used later for post-processing
        :param num_rel:
        :return:
        """
        available_edges = set([k for k, v in self.anc.family.items()]) - self.done_edges
        for edge in available_edges:
            story, proof_trace = self.derive([edge], k=self.num_rel-1)
            if len(story) == self.num_rel:
                id = str(uuid.uuid4())
                self.puzzles[id] = {
                    'edge': edge,
                    'story': story,
                    'proof': proof_trace
                }
                self.puzzles[id]['f_comb'] = '-'.join([self._get_edge_rel(x)['rel'] for x in story])
                self.puzzle_ct += 1


    def _value_counts(self):
        pztype = {}
        for pid, puzzle in self.puzzles.items():
            f_comb = puzzle['f_comb']
            if f_comb not in pztype:
                pztype[f_comb] = []
            pztype[f_comb].append(pid)
        return pztype

    def prune_puzzles(self, weight=None):
        """
        In order to keep all puzzles homogenously distributed ("f_comb"), we calcuate
        the count of all type of puzzles, and retain the minimum count
        :param weight: a dict of weights f_comb:p where 0 <= p <= 1
        :return:
        """
        pztype = self._value_counts()
        pztype_min_count = min([len(v) for k,v in pztype.items()])
        keep_puzzles = []
        for f_comb, pids in pztype.items():
            keep_puzzles.extend(random.sample(pids, pztype_min_count))
        not_keep = set(self.puzzles.keys()) - set(keep_puzzles)
        for pid in not_keep:
            del self.puzzles[pid]
        if weight:
            pztype = self._value_counts()
            # fill in missing weights
            for f_comb, pids in pztype.items():
                if f_comb not in weight:
                    weight[f_comb] = 1.0
            keep_puzzles = []
            for f_comb,pids in pztype.items():
                if weight[f_comb] == 1.0:
                    keep_puzzles.extend(pids)
            not_keep = set(self.puzzles.keys()) - set(keep_puzzles)
            for pid in not_keep:
                del self.puzzles[pid]

    def add_facts(self):
        """
            For each stored puzzle, add different types of facts
                - 1 : Provide supporting facts. After creating the essential fact graph, expand on any
                k number of edges (randomly)
                - 2: Irrelevant facts: after creating the relevant fact graph, expand on an edge,
                 but only provide dangling expansions
                - 3: Disconnected facts: along with relevant facts, provide a tree which is completely
                separate from the proof path
                - 4: Random attributes: school, place of birth, etc.
        :return:
        """
        for puzzle_id, puzzle in self.puzzles.items():
            if self.args.noise_support:
                # Supporting facts
                story = puzzle['story']
                extra_story = []
                for se in story:
                    e = self.expand(se)
                    if e:
                        if puzzle['edge'] not in e and len(set(e).intersection(set(story))) == 0 and len(set(e).intersection(set(extra_story))) == 0:
                            extra_story.extend(e)
                self.puzzles[puzzle_id]['fact_1'] = extra_story
            if self.args.noise_irrelevant:
                # Irrelevant facts
                story = puzzle['story']
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
            if self.args.noise_disconnected:
                # Disconnected facts
                story = puzzle['story']
                nodes_story = set([y for x in list(story) for y in x])
                nodes_not_in_story = set(self.anc.family_data.keys()) - nodes_story
                possible_edges = [(x,y) for x,y in it.combinations(list(nodes_not_in_story), 2) if (x,y) in self.anc.family]
                num_edges = random.choice(range(1, len(possible_edges)))
                possible_edges = random.sample(possible_edges, num_edges)
                self.puzzles[puzzle_id]['fact_3'] = possible_edges
            if self.args.noise_attributes:
                num_attr = random.choice(range(1, len(self.store.attribute_store)+1))
                story = puzzle['story']
                ents = [se[0] for se in story]
                ents.append(story[-1][-1])
                noise = []
                for ent in ents:
                    node = self.anc.family_data[ent]
                    n_att = [v for k,v in node.attributes.items()]
                    noise.extend(random.sample(n_att, num_attr))
                self.puzzles[puzzle_id]['text_fact_4'] = noise


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
                # format proof into human readable form
                e = self._format_edge_rel(e)
                ex_e = [self._format_edge_rel(x) for x in ex_e]
                proof_trace.append({e:ex_e})
                k = k-1
        return edge_list, proof_trace

    def _get_edge_rel(self, edge, rel_type='family'):
        # get node attributes
        node_b_attr = self.anc.family_data[edge[1]]
        relation = self.anc.family[edge][rel_type]
        edge_rel = self.relations_obj[relation][node_b_attr.gender]
        return edge_rel

    def _format_edge(self, edge):
        """
        Given an edge (x,y), format it into (name(x), name(y))
        :param edge:
        :return:
        """
        node_a_attr = self.anc.family_data[edge[0]]
        node_b_attr = self.anc.family_data[edge[1]]
        new_edge = (node_a_attr.name, node_b_attr.name)
        return new_edge

    def _format_edge_rel(self, edge, rel_type='family'):
        """
        Given an edge (x,y), format it into (name(x), rel(x,y), name(y))
        :param edge:
        :return:
        """
        node_a_attr = self.anc.family_data[edge[0]]
        node_b_attr = self.anc.family_data[edge[1]]
        edge_rel = self._get_edge_rel(edge, rel_type)['rel']
        new_edge = (node_a_attr.name, edge_rel, node_b_attr.name)
        return new_edge

    def stringify(self, edge, rel_type='family'):
        """
        Build story string from the edge
        :param edge: tuple
        :return:
        """
        # get node attributes
        node_a_attr = self.anc.family_data[edge[0]]
        node_b_attr = self.anc.family_data[edge[1]]
        relation = self._get_edge_rel(edge, rel_type)
        placeholders = relation['p']
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

    def generate_puzzles(self, weight=None):
        """
        Given stored puzzles, run `stringify` over them
        :param: extra_keys : this should contain the extra fact keys we want to add in the puzzles. We already generated
        the extra facts using `add_facts`, we just need to stringify them.
        :return:
        """
        self.prune_puzzles(weight)
        extra_keys = []
        if self.args.noise_support:
            extra_keys.append('fact_1')
        if self.args.noise_irrelevant:
            extra_keys.append('fact_2')
        if self.args.noise_disconnected:
            extra_keys.append('fact_3')
        puzzle_ids = self.puzzles.keys()
        for pi in puzzle_ids:
            self.puzzles[pi]['text_story'] = [self.stringify(e) for e in self.puzzles[pi]['story']]
            # either the target and query is reasoning from first and last, or memory retrieval from the given story
            if random.uniform(0,1) > self.args.memory:
                self.puzzles[pi]['query'] = self.puzzles[pi]['edge']
            else:
                self.puzzles[pi]['query'] = random.choice(self.puzzles[pi]['story'])
            # populate the target
            self.puzzles[pi]['target'] = self._get_edge_rel(self.puzzles[pi]['query'])['rel']
            self.puzzles[pi]['query_text'] = self._format_edge(self.puzzles[pi]['query'])
            self.puzzles[pi]['text_target'] = self.stringify(self.puzzles[pi]['query'])
            # populate the noise
            for key in extra_keys:
                self.puzzles[pi]['text_{}'.format(key)] = [self.stringify(e) for e in self.puzzles[pi][key]]
            # replace edges with name and relations
            self.puzzles[pi]['f_edge'] = self._format_edge_rel(self.puzzles[pi]['edge'])
            self.puzzles[pi]['f_story'] = [self._format_edge_rel(x) for x in self.puzzles[pi]['story']]

    def generate_question(self, query):
        """
        Given a query edge, generate a textual question from the question placeholder bank
        Use args.question to either generate a relational question or a yes/no question
        :param query:
        :return:
        """
        # TODO: return a question from the placeholder
        return ''


    def _test_story(self, story):
        """
        Given a list of edges of the story, test whether they are logically valid
        (x,y),(y,z) is valid, (x,y),(x,z) is not
        :param story: list of tuples
        :return:
        """
        for e_i in range(len(story) - 1):
            assert story[e_i][-1] == story[e_i + 1][0]

