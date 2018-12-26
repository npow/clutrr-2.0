# Generate story-summary pairs

from actors.ancestry import Ancestry
from relations.approx_builder import RelationBuilder
from tqdm import tqdm
import random
import pprint

from args import get_args
from utils.utils import split_train_test, write2file, sanity_check
from store.store import Store
import pandas as pd

#store = Store()

def generate_rows(args, store):
    # generate
    pb = tqdm(total=args.num_rows)
    num_stories = args.num_rows
    stories_left = num_stories
    columns = ['story', 'target', 'text_target', 'clean_story', 'proof_state']
    rows = []
    anc_num = 0
    while stories_left > 0:
        anc_num += 1
        anc = Ancestry(args, store)
        rb = RelationBuilder(args, store, anc)
        rb.build()
        rb.add_facts()
        rb.generate_puzzles()
        # now we have got the puzzles, add them to the story
        for pid, puzzle in rb.puzzles.items():
            story = puzzle['text_story']
            clean_story = ''.join(story)
            noise = [v for k,v in puzzle.items() if 'text_fact' in k]
            noise = [y for x in noise for y in x] # flatten
            story += noise
            story = random.sample(story, len(story))
            story = ''.join(story)
            rows.append([story, puzzle['target'], puzzle['text_target'], clean_story, puzzle['proof']])
            pb.update(1)
        stories_left = stories_left - len(rb.puzzles)
    pb.close()
    print("{} ancestries created".format(anc_num))
    return columns, rows


def current_config_path_stats(args):
    """
    Calculate the max path for the current configuration
    :return:
    """
    anc = Ancestry(max_levels=args.max_levels,
                   min_child=args.min_child,
                   max_child=args.max_child,
                   relationship_type=store.relationship_type)
    taken_names = anc.taken_names
    rb = RelationBuilder(boundary=args.boundary,
                         min_distractor_relations=args.min_distractor_relations,
                         backward=args.backward)
    rb.init_family(anc)
    all_paths, path_stats = rb.calc_all_pairs(num_relations=args.relation_length)
    path_rel = {}
    for path in all_paths:
        long_path = path[2]
        len_long_path = len(long_path)
        if len_long_path not in path_rel:
            path_rel[len_long_path] = []
        path_str = ''
        for mi in range(len_long_path - 1):
            na = long_path[mi]
            nb = long_path[mi + 1]
            weight = rb.inv_rel_type[rb.connected_family[na][nb]['weight']]
            if not rb.connected_forward.has_edge(na, nb) and weight not in ['sibling', 'SO']:
                weight = 'inv-' + weight
            path_str += ' -- <{}> -- '.format(weight)
        nb = long_path[len_long_path - 1]
        fw = rb.inv_rel_type[rb.connected_family[long_path[0]][nb]['weight']]
        path_str += ' ===> {}'.format(fw)
        path_rel[len_long_path].append(path_str)
    for key, val in path_rel.items():
        print("Relation length : {}".format(key - 1))
        uniq_paths = set(val)
        print("Unique paths : {}".format(len(uniq_paths)))
        print("With gender : {}".format(len(uniq_paths) * 2))
        if args.verbose:
            pprint.pprint(uniq_paths)
        #for up in uniq_paths:
        #    print(up, val.count(up))
    return path_stats


def test_run(args):
    store = Store(args)
    anc = Ancestry(args, store)
    rb = RelationBuilder(args, store, anc)
    rb.build()
    rb.add_facts()
    rb.generate_puzzles()
    print("Generated {} puzzles".format(len(rb.puzzles)))
    pid = random.choice(list(rb.puzzles.keys()))
    print(rb.puzzles[pid])

def main(args):
    store = Store(args)
    header, rows = generate_rows(args, store)
    df = pd.DataFrame(columns=header, data=rows)
    df.to_csv(args.output + '.csv')

if __name__ == '__main__':
    args = get_args()
    #test_run(args)
    main(args)








