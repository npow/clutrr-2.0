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

`python main.py --train_task 1.3 --test_tasks 1.3,1.4

You can provide general arguments as well, which are defined in the next section.

| Task | Description                              |
|------|------------------------------------------|
|   1  |   Basic family relations free of noise   |
|   2  |  Family relations with supporting facts  |
|   3  |  Family relations with irrelevant facts  |
|   4  | Family relations with disconnected facts |
|   5  |   Family relations with all facts (2-4)  |
|   6  |   Family relations with random attributes (v0.1 setup) |
|   7  | Family relations - Memory task: retrieve the relations already defined in text 
|   8  | Family relations - Mix of Memory and Reasoning - 1 & 7 |


Generated data is stored in `data/` folder.

## Generalizability

Each task mentioned above can be used for different length _k_ of the relations.
For example, Task 1 can have a train set of k=3 and test set of k=4,5,6, etc. See the
above section in how to provide such arguments quickly.


## General Usage

```
python generator.py
```

#### Usage

```
usage: main.py [-h] [--num_rows NUM_ROWS] [--max_levels MAX_LEVELS]
               [--min_child MIN_CHILD] [--max_child MAX_CHILD]
               [--p_marry P_MARRY] [--abstracts ABSTRACTS] [--boundary]
               [--output OUTPUT] [--relation_length RELATION_LENGTH]
               [--noise_support] [--noise_irrelevant] [--noise_disconnected]
               [--noise_attributes] [--rules_store RULES_STORE]
               [--relations_store RELATIONS_STORE]
               [--attribute_store ATTRIBUTE_STORE] [--train_task TRAIN_TASK]
               [--test_tasks TEST_TASKS] [--memory MEMORY]
               [--data_type DATA_TYPE] [--question QUESTION] [-v]
               [-t TEST_SPLIT]

optional arguments:
  -h, --help            show this help message and exit
  --num_rows NUM_ROWS   number of rows
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
  --train_task TRAIN_TASK
                        Define which task to create dataset for, including the
                        relationship length.
  --test_tasks TEST_TASKS
                        Define which tasks including the relation lengths to
                        test for, comma separaated
  --memory MEMORY       Percentage of tasks which are just memory retrieval
  --data_type DATA_TYPE
                        train/test
  --question QUESTION   Question type. 0 -> relational, 1 -> yes/no
  -v, --verbose         print the paths
  -t TEST_SPLIT, --test_split TEST_SPLIT
                        Testing split

```



## Author

Koustuv Sinha