# main file which defines the tasks
from args import get_args
from generator import main as gen_main

class Clutrr:
    def __init__(self, args):
        args = self._init_vars(args)
        self.run_task(args)

    def run_task(self, args):
        """
        Default dispatcher method
        """
        choice = args.task
        task_name = 'task_{}'.format(choice)
        task_method = getattr(self, task_name, lambda: "Task {} not implemented".format(choice))
        args = task_method(args)
        gen_main(args)

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

