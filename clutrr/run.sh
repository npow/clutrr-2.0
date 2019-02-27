#!/bin/sh

export CLUTRR_OUTPUT_DIR=data_new

# generalization tasks

python main.py --train_tasks 1.2,1.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - clean" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 2.2,2.3 --test_tasks 2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,2.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - support" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 3.2,3.3 --test_tasks 3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,3.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - noise a." --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 4.2,4.3 --test_tasks 4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,4.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - noise b." --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 5.2,5.3 --test_tasks 5.2,5.3,5.4,5.5,5.6,5.7,5.8,5.9,5.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - mix of support and noise" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 7.2,7.3 --test_tasks 7.2,7.3,7.4,7.5,7.6,7.7,7.8,7.9,7.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - memory" --output_dir $CLUTRR_OUTPUT_DIR

python main.py --train_tasks 1.2,1.4 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - clean" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 2.2,2.4 --test_tasks 2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,2.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - support" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 3.2,3.4 --test_tasks 3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,3.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - noise a." --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 4.2,4.4 --test_tasks 4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,4.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - noise b." --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 5.2,5.4 --test_tasks 5.2,5.3,5.4,5.5,5.6,5.7,5.8,5.9,5.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - mix of support and noise" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 7.2,7.4 --test_tasks 7.2,7.3,7.4,7.5,7.6,7.7,7.8,7.9,7.10 --train_rows 5000 --test_rows 100 --equal --data_name "Generalization - memory" --output_dir $CLUTRR_OUTPUT_DIR

python main.py --train_tasks 1.2,1.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 5000 --test_rows 100 --equal --holdout 1.3 --data_name "Generalization - holdout - clean" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 2.2,2.3 --test_tasks 2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,2.10 --train_rows 5000 --test_rows 100 --equal --holdout 2.3 --data_name "Generalization - holdout - support" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 3.2,3.3 --test_tasks 3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,3.10 --train_rows 5000 --test_rows 100 --equal --holdout 3.3 --data_name "Generalization - holdout - noise a." --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 4.2,4.3 --test_tasks 4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,4.10 --train_rows 5000 --test_rows 100 --equal --holdout 4.3 --data_name "Generalization - holdout - noise b." --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 5.2,5.3 --test_tasks 5.2,5.3,5.4,5.5,5.6,5.7,5.8,5.9,5.10 --train_rows 5000 --test_rows 100 --equal --holdout 5.3 --data_name "Generalization - holdout - mix of support and noise" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 7.2,7.3 --test_tasks 7.2,7.3,7.4,7.5,7.6,7.7,7.8,7.9,7.10 --train_rows 5000 --test_rows 100 --equal --holdout 7.3 --data_name "Generalization - holdout - memory" --output_dir $CLUTRR_OUTPUT_DIR


python main.py --train_tasks 1.2,1.3,1.4 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 3000 --test_rows 100 --equal --holdout 1.4 --data_name "Generalization - clean" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 2.2,2.3,2.4 --test_tasks 2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,2.10 --train_rows 3000 --test_rows 100 --equal --holdout 2.4 --data_name  "Generalization - support" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 3.2,3.3,3.4 --test_tasks 3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,3.10 --train_rows 3000 --test_rows 100 --equal --holdout 3.4 --data_name  "Generalization - noise a." --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 4.2,4.3,4.4 --test_tasks 4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,4.10 --train_rows 3000 --test_rows 100 --equal --holdout 4.4 --data_name "Generalization - noise b." --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 5.2,5.3,5.4 --test_tasks 5.2,5.3,5.4,5.5,5.6,5.7,5.8,5.9,5.10 --train_rows 3000 --test_rows 100 --equal --holdout 5.4 --data_name "Generalization - mix of support and noise" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 7.2,7.3,7.4 --test_tasks 7.2,7.3,7.4,7.5,7.6,7.7,7.8,7.9,7.10 --train_rows 3000 --test_rows 100 --equal --holdout 7.4 --data_name "Generalization - memory" --output_dir $CLUTRR_OUTPUT_DIR


# basic reasoning tasks

python main.py --train_tasks 1.2,1.3 --test_tasks 2.3,3.3,4.3,7.3 --train_rows 5000 --test_rows 100 --equal --data_name "Robust Reasoning - clean" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 2.2,2.3 --test_tasks 1.3,3.3,4.3,7.3 --train_rows 5000 --test_rows 100 --equal --data_name "Robust Reasoning - supporting" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 3.2,3.3 --test_tasks 1.3,2.3,4.3,7.3 --train_rows 5000 --test_rows 100 --equal --data_name "Robust Reasoning - noise a." --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 4.2,4.3 --test_tasks 1.3,2.3,3.3,7.3 --train_rows 5000 --test_rows 100 --equal --data_name "Robust Reasoning - noise b." --output_dir $CLUTRR_OUTPUT_DIR

python main.py --train_tasks 3.2,3.3,4.2,4.3 --test_tasks 1.3,2.3,7.3 --train_rows 2500 --test_rows 100 --equal --data_name "Robust Reasoning - noise a. and b." --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 1.2,1.3,4.2,4.3 --test_tasks 1.3,3.3,7.3 --train_rows 2500 --test_rows 100 --equal --data_name "Robust Reasoning - clean and noise b." --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 1.2,1.3,3.2,3.3 --test_tasks 1.3,4.3,7.3 --train_rows 2500 --test_rows 100 --equal --data_name "Robust Reasoning - clean and noise a." --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 1.2,1.3,7.2,7.3 --test_tasks 2.3,3.3,4.3 --train_rows 2500 --test_rows 100 --equal --data_name "Robust Reasoning - clean and memory" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 3.2,3.3,7.2,7.3 --test_tasks 1.3,2.3,4.3 --train_rows 2500 --test_rows 100 --equal --data_name "Robust Reasoning - noise a. and memory" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 4.2,4.3,7.2,7.3 --test_tasks 1.3,2.3,3.3 --train_rows 2500 --test_rows 100 --equal --data_name "Robust Reasoning - noise b. and memory" --output_dir $CLUTRR_OUTPUT_DIR


# how mixed training helps generalization

python main.py --train_tasks 3.2,3.3,4.2,4.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 2500 --test_rows 100 --equal --data_name "Generalization with Reasoning - noise a. and noise b." --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 1.2,1.3,4.2,4.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 2500 --test_rows 100 --equal --data_name "Generalization with Reasoning - clean and noise b." --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 1.2,1.3,3.2,3.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 2500 --test_rows 100 --equal --data_name "Generalization with Reasoning - clean and noise a." --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 1.2,1.3,7.2,7.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 2500 --test_rows 100 --equal --data_name "Generalization with Reasoning - clean and memory" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 3.2,3.3,7.2,7.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 2500 --test_rows 100 --equal --data_name "Generalization with Reasoning - noise a. and memory" --output_dir $CLUTRR_OUTPUT_DIR
python main.py --train_tasks 4.2,4.3,7.2,7.3 --test_tasks 1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,1.10 --train_rows 2500 --test_rows 100 --equal --data_name "Generalization with Reasoning - noise b. and memory" --output_dir $CLUTRR_OUTPUT_DIR



python utils/web.py --output_dir /private/home/koustuvs/clutrr/$CLUTRR_OUTPUT_DIR
