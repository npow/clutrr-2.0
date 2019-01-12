# main file which defines the tasks
from clutrr.args import get_args
from clutrr.generator import generate_rows
from clutrr.store.store import Store
from clutrr.utils.web import generate_webpage
import pandas as pd
import glob
import copy
import uuid
import os
import json
import shutil

class Clutrr:
    def __init__(self, args):
        args = self._init_vars(args)
        self.run_task(args)

    def generate(self, choice, args, num_rows=0, data_type='train'):
        """
        Choose the task and the relation length
        Return the used args for storing
        :param choice:
        :param args:
        :param num_rows:
        :param data_type:
        :return:
        """
        args = copy.deepcopy(args)
        args.num_rows = num_rows
        args.data_type = data_type
        task, relation_length = choice.split('.')
        task_name = 'task_{}'.format(task)
        task_method = getattr(self, task_name, lambda: "Task {} not implemented".format(choice))
        args = task_method(args)
        args.relation_length = int(relation_length)
        store = Store(args)
        return (generate_rows(args, store, task_name), args)

    def run_task(self, args):
        """
        Default dispatcher method
        """
        total_rows = args.num_rows
        train_rows = int(args.num_rows * (1-args.test_split))
        test_rows = total_rows - train_rows
        train_choice = args.train_task
        test_choices = args.test_tasks.split(',')
        # training
        train_data = self.generate(train_choice, args, num_rows=train_rows, data_type='train')
        test_datas = []
        for t_choice in test_choices:
            test_datas.append(self.generate(t_choice, args, num_rows=test_rows, data_type='test'))
        self.store(train_data, test_datas, args)

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
        train_rows, train_args = train_data
        train_df = pd.DataFrame(columns=train_rows[0], data=train_rows[1])
        all_config = {}
        train_fl_name = self.assign_name(train_args, args.train_task)
        all_config['train_task'] = {args.train_task: train_fl_name}
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
            test_dfs.append(pd.DataFrame(columns=test_rows[0], data=test_rows[1]))
            all_config['test_tasks'][test_tasks[i]] = tname
        base_path = os.path.abspath(os.pardir)
        # derive folder name as a random selection of characters
        directory = ''
        while True:
            folder_name = 'data_{}'.format(str(uuid.uuid4())[:8])
            directory = os.path.join(base_path, 'data', folder_name)
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

        print("Created dataset in {}".format(directory))
        self.analyze_data(directory)

    def analyze_data(self, directory):
        all_files = glob.glob(os.path.join(directory,'*.csv'))
        for fl in all_files:
            print("Analyzing file {}".format(fl))
            df = pd.read_csv(fl)
            uniq_patterns = len(df['f_comb'].value_counts())
            print("-> {} rows".format(len(df)))
            print("-> {} unique patterns".format(uniq_patterns))
            if '_train' in fl:
                print(df['f_comb'].value_counts().to_string())
        print("Analysis complete")

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

    def task_6(self, args):
        """
        Family relation with random attributes (v0.1 setup)
        """
        args.noise_attributes = True
        args.output += '_task6'
        return args

    def task_7(self, args):
        """
        Family relation with only memory retrieval
        :param args:
        :return:
        """
        args.memory = 1.0
        args.output += '_task7'
        return args

    def task_8(self, args):
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
    Clutrr(args)
    generate_webpage('/home/mlp/ksinha4/clutrr/data')
