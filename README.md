## CLUTRR

**C**ompositional **L**anguage **U**nderstanding with **T**ext-based **R**elational **R**easoniong

A benchmark dataset generator to test relational reasoning on text

### Dependencies

- [pandas](https://pypi.org/project/pandas/) - to store and retrieve in csv
- [names](https://pypi.org/project/names/) - to generate fancy names
- [tqdm](https://pypi.org/project/tqdm/) - for fancy progressbars

## Tasks

CLUTRR is highly modular and thus can be used for various different probing tasks. Here we document the various types of tasks
available and the corresponding config arguments to generate them. To
run a task, refer the following table and run:

`python main.py --train_task <> --test_tasks <> <args>`

Where, `train_task` is in the form of `<task_id>.<relation_length>`, and `test_tasks` is a comma separated list of the same form. For eg:

`python main.py --train_tasks 1.3 --test_tasks 1.3,1.4`

You can provide general arguments as well, which are defined in the next section.

| Task | Description                              |
|------|------------------------------------------|
|   1  | Basic family relations free of noise   |
|   2  | Family relations with supporting facts  |
|   3  | Family relations with irrelevant facts  |
|   4  | Family relations with disconnected facts |
|   5  | Family relations with all facts (2-4)  |
|   6  | Family relations - Memory task: retrieve the relations already defined in text 
|   7  | Family relations - Mix of Memory and Reasoning - 1 & 6 |   


Generated data is stored in `data/` folder.

## Generalizability

Each task mentioned above can be used for different length _k_ of the relations.
For example, Task 1 can have a train set of k=3 and test set of k=4,5,6, etc. See the
above section in how to provide such arguments quickly.


## AMT Paraphrasing

We collect paraphrases for relations k=1,2 and 3 from Amazon Mechanical Turk using [ParlAI](https://github.com/facebookresearch/parlai)
MTurk interface. The collected paraphrases can be re-used as _templates_ to generate
arbitrary large dataset in the above configurations. We will release the templates shortly here.

To use the templates, pass `--use_mturk_template` flag and location of the template using 
`--template_file` argument. The flag `--template_length` is optional and it governs
the maximum length k to use to replace the sentences.

## Rules

We create an ideal simple kinship world, which are derived from a set of _clauses_ or rules.
The rules are defined in [rules_store.yaml](clutrr/store/rules_store.yaml) file.


#### Usage

```
usage: main.py [-h] [--max_levels MAX_LEVELS] [--min_child MIN_CHILD]
               [--max_child MAX_CHILD] [--p_marry P_MARRY]
               [--abstracts ABSTRACTS] [--boundary] [--output OUTPUT]
               [--relation_length RELATION_LENGTH] [--noise_support]
               [--noise_irrelevant] [--noise_disconnected]
               [--noise_attributes] [--rules_store RULES_STORE]
               [--relations_store RELATIONS_STORE]
               [--attribute_store ATTRIBUTE_STORE] [--train_tasks TRAIN_TASKS]
               [--test_tasks TEST_TASKS] [--train_rows TRAIN_ROWS]
               [--test_rows TEST_ROWS] [--memory MEMORY]
               [--data_type DATA_TYPE] [--question QUESTION] [-v]
               [-t TEST_SPLIT] [--equal] [--analyze] [--mturk]
               [--holdout HOLDOUT] [--data_name DATA_NAME]
               [--use_mturk_template] [--template_length TEMPLATE_LENGTH]
               [--template_file TEMPLATE_FILE] [--output_dir OUTPUT_DIR]

optional arguments:
  -h, --help            show this help message and exit
  --max_levels MAX_LEVELS
                        max number of levels
  --min_child MIN_CHILD
                        max number of children per node
  --max_child MAX_CHILD
                        max number of children per node
  --p_marry P_MARRY     Probability of marriage among nodes
  --abstracts ABSTRACTS
                        Abstract lines per relation
  --boundary            Boundary in entities
  --output OUTPUT       Prefix of the output file
  --relation_length RELATION_LENGTH
                        Max relation path length
  --noise_support       Noise type: Supporting facts
  --noise_irrelevant    Noise type: Irrelevant facts
  --noise_disconnected  Noise type: Disconnected facts
  --noise_attributes    Noise type: Random attributes
  --rules_store RULES_STORE
                        Rules store
  --relations_store RELATIONS_STORE
                        Relations store
  --attribute_store ATTRIBUTE_STORE
                        Attributes store
  --train_tasks TRAIN_TASKS
                        Define which task to create dataset for, including the
                        relationship length, comma separated
  --test_tasks TEST_TASKS
                        Define which tasks including the relation lengths to
                        test for, comma separaated
  --train_rows TRAIN_ROWS
                        number of train rows
  --test_rows TEST_ROWS
                        number of test rows
  --memory MEMORY       Percentage of tasks which are just memory retrieval
  --data_type DATA_TYPE
                        train/test
  --question QUESTION   Question type. 0 -> relational, 1 -> yes/no
  -v, --verbose         print the paths
  -t TEST_SPLIT, --test_split TEST_SPLIT
                        Testing split
  --equal               Make sure each pattern is equal. Warning: Time
                        complexity of generation increases if this flag is
                        set.
  --analyze             Analyze generated files
  --mturk               prepare data for mturk
  --holdout HOLDOUT     if true, then hold out unique patterns in the test set
  --data_name DATA_NAME
                        Dataset name
  --use_mturk_template  use the templating data for mturk
  --template_length TEMPLATE_LENGTH
                        Max Length of the template to substitute
  --template_file TEMPLATE_FILE
                        location of placeholders
  --output_dir OUTPUT_DIR
                        output_dir
```



## Author

Koustuv Sinha