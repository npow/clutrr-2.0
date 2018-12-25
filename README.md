## CLUTRR

**C**ompositional **L**anguage **U**nderstanding with **T**ext-based **R**elational **R**easoniong

A benchmark dataset generator to test relational reasoning on text

### Dependencies

- [NetworkX](https://networkx.github.io/)
- [pandas](https://pypi.org/project/pandas/)
- [names](https://pypi.org/project/names/)
- [tqdm](https://pypi.org/project/tqdm/)

### Generate

```
python generator.py
```

#### Usage

```
usage: generator.py [-h] [--num_rows NUM_ROWS] [--max_levels MAX_LEVELS]
                    [--min_child MIN_CHILD] [--max_child MAX_CHILD]
                    [--p_marry P_MARRY] [--abstracts ABSTRACTS] [--boundary]
                    [--output OUTPUT] [--relation_length RELATION_LENGTH]
                    [--noise_support] [--noise_irrelevant]
                    [--noise_disconnected] [--rules_store RULES_STORE]
                    [--relations_store RELATIONS_STORE]
                    [--attribute_store ATTRIBUTE_STORE] [-v]

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
  --rules_store RULES_STORE
                        Rules store
  --relations_store RELATIONS_STORE
                        Relations store
  --attribute_store ATTRIBUTE_STORE
                        Attributes store
  -v, --verbose         print the paths

```

## Tasks

CLUTRR is highly modular and thus can be used for various different probing tasks. Here we document the various types of tasks
available and the corresponding config arguments to generate them.



## Author

Koustuv Sinha