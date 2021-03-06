# main file which defines the tasks
from clutrr.args import get_args
from clutrr.generator import generate_rows
from clutrr.store.store import Store
import pandas as pd
import glob
import copy
import uuid
import os
import json
import shutil
import sys
from nltk.tokenize import word_tokenize

logPath = '../logs/'
fileName = 'data'

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger()

class Clutrr:
    def __init__(self, args):
        args = self._init_vars(args)
        self.run_task(args)

    def generate(self, choice, args, num_rows=0, data_type='train', multi=False):
        """
        Choose the task and the relation length
        Return the used args for storing
        :param choice:
        :param args:
        :param num_rows:
        :param data_type:
        :param multi:
        :return:
        """
        args = copy.deepcopy(args)
        args.num_rows = num_rows
        args.data_type = data_type
        if not multi:
            task, relation_length = choice.split('.')
            task_name = 'task_{}'.format(task)
            logger.info("mode : {}, task : {}, rel_length : {}".format(data_type, task_name, relation_length))
            task_method = getattr(self, task_name, lambda: "Task {} not implemented".format(choice))
            args = task_method(args)
            args.relation_length = int(relation_length)
            store = Store(args)
            return (generate_rows(args, store, task_name  + '.{}'.format(relation_length)), args)
        else:
            rows = []
            columns = []
            for ch in choice:
                task, relation_length = ch.split('.')
                task_name = 'task_{}'.format(task)
                logger.info("mode : {}, task : {}, rel_length : {}".format(data_type, task_name, relation_length))
                task_method = getattr(self, task_name, lambda: "Task {} not implemented".format(choice))
                args = task_method(args)
                args.relation_length = int(relation_length)
                store = Store(args)
                columns,r = generate_rows(args, store, task_name + '.{}'.format(relation_length))
                rows.extend(r)
            return ((columns, rows), args)

    def run_task(self, args):
        """
        Default dispatcher method
        """
        train_rows = args.train_rows
        test_rows = args.test_rows
        train_choices = args.train_tasks.split(',')
        test_choices = args.test_tasks.split(',')
        # training
        train_datas = []
        for t_choice in train_choices:
            train_datas.append(self.generate(t_choice, args, num_rows=train_rows, data_type='train'))
        test_datas = []
        for t_choice in test_choices:
            test_datas.append(self.generate(t_choice, args, num_rows=test_rows, data_type='test'))
        self.store(train_datas, test_datas, args)

    def assign_name(self, args, task_name):
        """
        Create a name for the datasets:
            - training file should end with _train
            - testing file should end with _test
            - each file name should have an unique hex
        :param args:
        :return:
        """
        #hex = str(uuid.uuid4())[:8]
        name = '{}_{}.csv'.format(task_name, args.data_type)
        return name

    def store(self, train_data, test_data, args):
        """
        Take the dataset and do the following:
        - Create a name for the files
        - Create a folder and put the files in
        - Write the config in a file and put it in the folder
        - Compute the hash of the train and test files and store it in a file
        :param train_data list of rows
        :param test_data list of list of rows
        :return:
        """
        train_tasks = args.train_tasks.split(',')
        train_df = []
        holdout = []
        train_args = None
        for i, td in enumerate(train_data):
            train_rows, train_args = td
            tdf = pd.DataFrame(columns=train_rows[0], data=train_rows[1])
            if args.holdout == train_tasks[i]:
                logger.info("holding out train {}".format(train_tasks[i]))
                f_combs = tdf['f_comb'].value_counts().index.tolist()
                split = int(len(f_combs) * (1 - args.test_split))
                f_comb_train = f_combs[:split]
                f_comb_test = f_combs[split:]
                logger.info("patterns in train : {}".format(len(f_comb_train)))
                logger.info("patterns in test : {}".format(len(f_comb_test)))
                holdout.append(tdf[tdf['f_comb'].isin(f_comb_test)])
                tdf = tdf[tdf['f_comb'].isin(f_comb_train)]
            train_df.append(tdf)

        train_df = pd.concat(train_df)
        logger.info("Training rows : {}".format(len(train_df)))
        all_config = {}
        train_fl_name = self.assign_name(train_args, args.train_tasks)
        all_config['train_task'] = {args.train_tasks: train_fl_name}
        all_config['test_tasks'] = {}
        test_fl_names = []
        test_dfs = []
        all_config['args'] = {}
        all_config['args'][train_fl_name] = vars(train_args)
        test_tasks = args.test_tasks.split(',')
        for i,td in enumerate(test_data):
            test_rows, test_args = td
            tname = self.assign_name(test_args, test_tasks[i])
            test_fl_names.append(tname)
            all_config[tname] = vars(test_args)
            if args.holdout == test_tasks[i]:
                logger.info("saving hold out test {}".format(test_tasks[i]))
                test_dfs.append(holdout[0])
            else:
                test_dfs.append(pd.DataFrame(columns=test_rows[0], data=test_rows[1]))
            all_config['test_tasks'][test_tasks[i]] = tname

        base_path = os.path.abspath(os.pardir)
        # derive folder name as a random selection of characters
        directory = ''
        while True:
            folder_name = 'data_{}'.format(str(uuid.uuid4())[:8])
            directory = os.path.join(base_path, args.output_dir, folder_name)
            if not os.path.exists(directory):
                os.makedirs(directory)
                break
        train_df.to_csv(os.path.join(directory, train_fl_name))
        for i,test_fl_name in enumerate(test_fl_names):
            test_df = test_dfs[i]
            test_df.to_csv(os.path.join(directory, test_fl_name))
        # dump config
        json.dump(all_config, open(os.path.join(directory, 'config.json'),'w'))
        shutil.make_archive(directory, 'zip', directory)

        logger.info("Created dataset in {}".format(directory))
        self.analyze_data(directory)
        if args.mturk:
            self.keep_unique(directory)


    def analyze_data(self, directory):
        all_files = glob.glob(os.path.join(directory,'*.csv'))
        for fl in all_files:
            logger.info("Analyzing file {}".format(fl))
            df = pd.read_csv(fl)
            df['word_len'] = df.story.apply(lambda x: len(word_tokenize(x)))
            df['word_len_clean'] = df.clean_story.apply(lambda x: len(word_tokenize(x)))
            print("Max words : ", df.word_len.max())
            print("Min words : ", df.word_len.min())
            print("For clean story : ")
            print("Max words : ", df.word_len_clean.max())
            print("Min words : ", df.word_len_clean.min())
            #uniq_patterns = len(df['f_comb'].value_counts())
            #logger.info("-> {} rows".format(len(df)))
            #logger.info("-> {} unique patterns".format(uniq_patterns))
            #if '_train' in fl:
            #    logger.info(df['f_comb'].value_counts().to_string())
        logger.info("Analysis complete")

    def keep_unique(self, directory, num=1):
        """
        Keep num unique rows for each pattern. Handy for Mturk collection.
        :param num:
        :return:
        """
        all_files = glob.glob(os.path.join(directory, '*.csv'))
        for fl in all_files:
            df = pd.read_csv(fl)
            uniq_patterns = df['f_comb'].unique()
            udf = []
            for up in uniq_patterns:
                # randomly select one row for this unique pattern
                rd = df[df['f_comb'] == up].sample(num)
                udf.append(rd)
            udf = pd.concat(udf)
            udf.to_csv(fl)



    def _init_vars(self, args):
        args.noise_support = False
        args.noise_irrelevant = False
        args.noise_disconnected = False
        args.noise_attributes = False
        args.memory = 0
        return args

    def task_1(self, args):
        """
        Basic family relation without any noise
        :return:
        """
        args.output += '_task1'
        return args

    def task_2(self, args):
        """
        Family relation with supporting facts
        :return:
        """
        args.noise_support = True
        args.output += '_task2'
        return args

    def task_3(self, args):
        """
        Family relation with irrelevant facts
        :return:
        """
        args.noise_irrelevant = True
        args.output += '_task3'
        return args

    def task_4(self, args):
        """
        Family relation with disconnected facts
        :return:
        """
        args.noise_disconnected = True
        args.output += '_task4'
        return args

    def task_5(self, args):
        """
        Family relation with all facts
        :return:
        """
        args.noise_support = True
        args.noise_disconnected = True
        args.noise_disconnected = True
        args.output += '_task5'
        return args

    # Deprecated task
    # def task_6(self, args):
    #     """
    #     Family relation with random attributes (v0.1 setup)
    #     """
    #     args.noise_attributes = True
    #     args.output += '_task6'
    #     return args

    def task_6(self, args):
        """
        Family relation with only memory retrieval
        :param args:
        :return:
        """
        args.memory = 1.0
        args.output += '_task7'
        return args

    def task_7(self, args):
        """
        Family relation with mixed memory and reasoning
        :param args:
        :return:
        """
        args.memory = 0.5
        args.output += '_task8'
        return args


if __name__ == '__main__':
    args = get_args()
    logger.info("Data generation started for configurations : ")
    logger.info('\ntogrep : {0}\n'.format(sys.argv[1:]))
    Clutrr(args)
    logger.info("\ntogrep : Data generation done {0}\n".format(sys.argv[1:]))
    logger.info("-----------------------------------------------------")
