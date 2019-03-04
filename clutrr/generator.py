# Generate story-summary pairs

from clutrr.actors.ancestry import Ancestry
from clutrr.relations.builder import RelationBuilder
from tqdm import tqdm
import random
import numpy as np
import json
import copy

from clutrr.args import get_args
from clutrr.store.store import Store
from clutrr.utils.utils import comb_indexes
import pandas as pd

#store = Store()

class TemplateUser:
    """
    Replaces story with the templates obtained from AMT
    """
    def __init__(self, templates, family):
        self.templates = copy.copy(templates)
        self.family = family # dict containing node informations
        self.used_template = ''
        self.entity_id_dict = {}
        self.seen_ent = set()

    def choose_template(self, f_comb, entities, verbose=False):
        """
        Choose a template to use. Do not use the same template in this current context
        :return:
        """
        self.entity_id_dict = {}
        self.seen_ent = set()
        gender_comb = []
        # build the dictionary of entity - ids
        for ent in entities:
            if ent not in self.seen_ent:
                gender_comb.append(self.family[ent].gender)
                self.seen_ent.add(ent)
                self.entity_id_dict[ent] = len(self.entity_id_dict)
        gender_comb = '-'.join(gender_comb)
        if verbose:
            print(f_comb)
            print(gender_comb)
            print(len(self.templates[f_comb][gender_comb]))
        if len(self.templates[f_comb][gender_comb]) == 0:
            raise NotImplementedError("template combination not found.")
        available_templates = self.templates[f_comb][gender_comb]
        chosen_template = random.choice(available_templates)
        self.used_template = chosen_template
        used_i = self.templates[f_comb][gender_comb].index(chosen_template)
        # remove the used template
        # del self.templates[f_comb][gender_comb][used_i]
        return chosen_template


    def replace_template(self, f_comb, entities, verbose=False):
        chosen_template = self.choose_template(f_comb, entities, verbose=verbose)

        for ent_id, ent in enumerate(list(set(entities))):
            node = self.family[ent]
            gender = node.gender
            name = node.name
            chosen_template = chosen_template.replace('ENT_{}_{}'.format(self.entity_id_dict[ent], gender), '[{}]'.format(name))
        return chosen_template


def generate_rows(args, store, task_name):
    # generate
    print(args.relation_length)
    print("Loading templates...")
    templates = json.load(open(args.template_file))
    pb = tqdm(total=args.num_rows)
    num_stories = args.num_rows
    stories_left = num_stories
    columns = ['id', 'story', 'query', 'text_query', 'target', 'text_target', 'clean_story', 'proof_state', 'f_comb', 'task_name', 'story_edges','edge_types','query_edge','genders', 'syn_story']
    f_comb_count = {}
    rows = []
    anc_num = 0
    anc_num += 1
    anc = Ancestry(args, store)
    rb = RelationBuilder(args, store, anc)
    while stories_left > 0:
        status = rb.build()
        if not status:
            rb.reset_puzzle()
            rb.anc.next_flip()
            continue
        rb.add_facts()
        # keeping a count of generated patterns to make sure we have homogenous distribution
        if len(f_comb_count) > 0 and args.equal:
            min_c = min([v for k,v in f_comb_count.items()])
            weight = {k:(min_c/v) for k,v in f_comb_count.items()}
            rb.generate_puzzles(weight)
        else:
            rb.generate_puzzles()
        # now we have got the puzzles, add them to the story
        for pid, puzzle in rb.puzzles.items():
            story_edges = puzzle['text_story']       # dict of edge:text
            clean_story = ''.join([puzzle['text_story'][e] for e in story_edges])
            noise_edge_list = [v for k,v in puzzle.items() if 'text_fact' in k]
            for d in noise_edge_list:
                if type(d) != dict:
                    print(d)
                    print(noise_edge_list)
                    raise AssertionError()
                story_edges.update(d)          # adds the noise edge:text
            #noise = [y for x in noise for y in x] # flatten
            #story += noise
            story_keys = random.sample(list(story_edges.keys()), len(story_edges))
            story = ''.join([story_edges[k] for k in story_keys])
            story_key_edges = [rb.get_edge_relation(k) for k in story_keys]
            all_edge_rows = []
            all_edge_rows.append(puzzle['story'])
            all_edge_rows.extend(puzzle['all_noise'])

            # Templating Logic
            # all_edge_rows = list of two list : [story, noise]
            # where, story = list of edges, noise = list of edges
            # story and noise = sequence

            templated_rows = []
            if args.use_mturk_template:
                for seq in all_edge_rows:
                    #print(seq)
                    # find all grouping combinations
                    group_combs = comb_indexes(seq, args.template_length)
                    #print(group_combs)
                    temp_rows = []
                    temp_user = TemplateUser(templates=templates, family=rb.anc.family_data)
                    for group in group_combs:
                        try:
                            fcombs = ['-'.join([rb.get_edge_relation(edge) for edge in edge_group]) for edge_group in group]
                            fentities = [[ent for edge in edge_group for ent in edge] for edge_group in group]
                            prows = [temp_user.replace_template(edge_group, fentities[group_id])
                                for group_id, edge_group in enumerate(fcombs)]
                            temp_rows.append((group, prows))
                        except:
                            pass
                    #print(len(temp_rows))
                    if len(temp_rows) == 0:
                        print(group_combs)
                        print(all_edge_rows)
                        print(seq)
                        fcombs = ['-'.join([rb.get_edge_relation(edge) for edge in edge_group]) for edge_group in group]
                        fentities = [[ent for edge in edge_group for ent in edge] for edge_group in group]
                        prows = [temp_user.replace_template(edge_group, fentities[group_id], verbose=True)
                                 for group_id, edge_group in enumerate(fcombs)]
                    chosen_row = random.choice(temp_rows)
                    #print('chosen row', chosen_row)
                    templated_rows.append(chosen_row)

                templated_rows = [row[-1] for row in templated_rows]
                # flatten
                templated_rows = [xt for t in templated_rows for xt in t]

            ## The same thing above without the try catch block
            '''
            random_combs = [choose_random_subsequence(ae, args.template_length) for ae in all_edge_rows]
            random_f_combs = [['-'.join([rb.get_edge_relation(edge) for edge in cr]) for cr in row] for row in random_combs]
            random_entities = [[[e for edge in cr for e in edge] for cr in row] for row in random_combs]
            placed_rows = [[replace_template(templates, cr, random_entities[row_id][c_id], rb.anc.family_data)
                            for c_id, cr in enumerate(row)] for row_id,row in enumerate(random_f_combs)]
            print('a',all_edge_rows)
            print(random_combs)
            print(random_f_combs)
            print(random_entities)
            '''
            # convert edge list into e_0, e_1
            node_ct = 0
            node_id_dict = {}
            for key in story_keys:
                if key[0] not in node_id_dict:
                    node_id_dict[key[0]] = node_ct
                    node_ct +=1
                if key[1] not in node_id_dict:
                    node_id_dict[key[1]] = node_ct
                    node_ct +=1
            story_keys_changed_id = [(node_id_dict[key[0]], node_id_dict[key[1]]) for key in story_keys]
            # add the query edges with respect to the same id
            query_edge = (node_id_dict[puzzle['query'][0]], node_id_dict[puzzle['query'][1]])
            text_question = rb.generate_question(puzzle['query'])
            # also store the gender for postprocessing
            genders = ','.join(['{}:{}'.format(rb.anc.family_data[node_id].name,
                                               rb.anc.family_data[node_id].gender)
                                for node_id in node_id_dict.keys()])
            if puzzle['f_comb'] not in f_comb_count:
                f_comb_count[puzzle['f_comb']] = 0
            f_comb_count[puzzle['f_comb']] +=1
            stories_left -= 1
            if stories_left < 0:
                break

            syn_story = ''
            if args.use_mturk_template:
                syn_story = story
                story = ' '.join(templated_rows)
            rows.append([pid, story, puzzle['query_text'], text_question, puzzle['target'], puzzle['text_target'],
                         clean_story, puzzle['proof'], puzzle['f_comb'], task_name, story_keys_changed_id,
                         story_key_edges, query_edge, genders, syn_story])
            pb.update(1)
        rb.reset_puzzle()
        rb.anc.next_flip()
    pb.close()
    print("{} ancestries created".format(anc_num))
    print("Number of unique patterns : {}".format(len(f_comb_count)))
    return columns, rows


def test_run(args):
    store = Store(args)
    anc = Ancestry(args, store)
    rb = RelationBuilder(args, store, anc)
    rb.num_rel = 3
    all_patterns = set()
    while True:
        for j in range(len(anc.family_data.keys())):
            rb.build()
            up = rb.unique_patterns()
            all_patterns.update(up)
            print(len(all_patterns))
            rb.reset_puzzle()
        if not rb.anc.next_flip():
            break
    print("Number of unique puzzles : {}".format(len(all_patterns)))

    rb.add_facts()
    rb.generate_puzzles()
    print("Generated {} puzzles".format(len(rb.puzzles)))
    pid = random.choice(list(rb.puzzles.keys()))
    print(rb.puzzles[pid])

def main(args):
    store = Store(args)
    header, rows = generate_rows(args, store)
    df = pd.DataFrame(columns=header, data=rows)
    # split test train
    msk = np.random.rand(len(df)) > args.test
    train_df = df[msk]
    test_df = df[~msk]
    train_df.to_csv(args.output + '_train.csv')
    test_df.to_csv(args.output + '_test.csv')

if __name__ == '__main__':
    args = get_args()
    test_run(args)
    #main(args)








