# Generate story-summary pairs

from actors.ancestry import Ancestry
from relations.builder import RelationBuilder
from tqdm import tqdm
import random
import numpy as np

from args import get_args
from store.store import Store
import pandas as pd

#store = Store()

def generate_rows(args, store):
    # generate
    pb = tqdm(total=args.num_rows)
    num_stories = args.num_rows
    stories_left = num_stories
    columns = ['id', 'story', 'query', 'text_query', 'target', 'text_target', 'clean_story', 'proof_state']
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
            text_question = rb.generate_question(puzzle['query'])
            rows.append([pid, story, puzzle['query_text'], text_question, puzzle['target'], puzzle['text_target'],
                         clean_story, puzzle['proof']])
            pb.update(1)
        stories_left = stories_left - len(rb.puzzles)
    pb.close()
    print("{} ancestries created".format(anc_num))
    return columns, rows


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
    # split test train
    msk = np.random.rand(len(df)) > args.test
    train_df = df[msk]
    test_df = df[~msk]
    train_df.to_csv(args.output + '_train.csv')
    test_df.to_csv(args.output + '_test.csv')

if __name__ == '__main__':
    args = get_args()
    #test_run(args)
    main(args)








