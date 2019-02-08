import argparse

def get_args():
    parser = argparse.ArgumentParser()
    # graph parameters
    parser.add_argument("--max_levels", default=2, type=int, help="max number of levels")
    parser.add_argument("--min_child", default=4, type=int, help="max number of children per node")
    parser.add_argument("--max_child", default=4, type=int, help="max number of children per node")
    parser.add_argument("--p_marry", default=1.0, type=float, help="Probability of marriage among nodes")
    # story parameters
    parser.add_argument("--abstracts", default=1, type=int, help="Abstract lines per relation")
    parser.add_argument("--boundary",default=True, action='store_true', help='Boundary in entities')
    parser.add_argument("--output", default="gen_m3", type=str, help='Prefix of the output file')
    parser.add_argument("--relation_length", default=3, type=int, help="Max relation path length")
    # noise choices
    parser.add_argument("--noise_support", default=False, action='store_true',
                        help="Noise type: Supporting facts")
    parser.add_argument("--noise_irrelevant", default=False, action='store_true',
                        help="Noise type: Irrelevant facts")
    parser.add_argument("--noise_disconnected", default=False, action='store_true',
                        help="Noise type: Disconnected facts")
    parser.add_argument("--noise_attributes", default=False, action='store_true',
                        help="Noise type: Random attributes")
    # store locations
    parser.add_argument("--rules_store", default="rules_store.yaml", type=str, help='Rules store')
    parser.add_argument("--relations_store", default="relations_store.yaml", type=str, help='Relations store')
    parser.add_argument("--attribute_store", default="attribute_store.json", type=str, help='Attributes store')
    # task
    parser.add_argument("--train_task", default="1.3", type=str, help='Define which task to create dataset for, including the relationship length.')
    parser.add_argument("--test_tasks", default="1.3", type=str, help='Define which tasks including the relation lengths to test for, comma separaated')
    parser.add_argument("--train_rows", default=100, type=int, help='number of train rows')
    parser.add_argument("--test_rows", default=100, type=int, help='number of test rows')
    parser.add_argument("--memory", default=1, type=float, help='Percentage of tasks which are just memory retrieval')
    parser.add_argument("--data_type", default="train", type=str, help='train/test')
    # question type
    parser.add_argument("--question", default=0, type=int, help='Question type. 0 -> relational, 1 -> yes/no')
    # others
    # TODO: do we want to keep the old method of adding distractors?
    # parser.add_argument("--min_distractor_relations", default=8, type=int, help="Distractor relations about entities")
    parser.add_argument("-v","--verbose", default=False, action='store_true',
                        help='print the paths')
    parser.add_argument("-t","--test_split", default=0.2, help="Testing split")
    parser.add_argument("--equal", default=False, action='store_true',
                        help="Make sure each pattern is equal. Warning: Time complexity of generation increases if this flag is set.")
    parser.add_argument("--analyze", default=False, action='store_true', help="Analyze generated files")
    parser.add_argument("--mturk", default=False, action='store_true', help='prepare data for mturk')


    return parser.parse_args()