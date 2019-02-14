# Generate story-summary pairs

from clutrr.actors.ancestry import Ancestry
from clutrr.relations.builder import RelationBuilder
from tqdm import tqdm
import random
import numpy as np

from clutrr.args import get_args
from clutrr.store.store import Store
import pandas as pd

#store = Store()

def generate_rows(args, store, task_name):
    # generate
    print(args.relation_length)
    pb = tqdm(total=args.num_rows)
    num_stories = args.num_rows
    stories_left = num_stories
    columns = ['id', 'story', 'query', 'text_query', 'target', 'text_target', 'clean_story', 'proof_state', 'f_comb', 'task_name']
    f_comb_count = {}
    rows = []
    anc_num = 0
    anc_num += 1
    anc = Ancestry(args, store)
    rb = RelationBuilder(args, store, anc)
    while stories_left > 0:
        rb.build()
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
            story = puzzle['text_story']
            clean_story = ''.join(story)
            noise = [v for k,v in puzzle.items() if 'text_fact' in k]
            noise = [y for x in noise for y in x] # flatten
            story += noise
            story = random.sample(story, len(story))
            story = ''.join(story)
            text_question = rb.generate_question(puzzle['query'])
            if puzzle['f_comb'] not in f_comb_count:
                f_comb_count[puzzle['f_comb']] = 0
            f_comb_count[puzzle['f_comb']] +=1
            stories_left -= 1
            if stories_left < 0:
                break
            rows.append([pid, story, puzzle['query_text'], text_question, puzzle['target'], puzzle['text_target'],
                         clean_story, puzzle['proof'], puzzle['f_comb'], task_name])
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








