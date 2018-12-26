# main file which defines the tasks
from args import get_args
from generator import main as gen_main

class Clutrr:
    def __init__(self, args):
        args = self._invalidate_noise(args)
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

    def _invalidate_noise(self, args):
        args.noise_support = False
        args.noise_irrelevant = False
        args.noise_disconnected = False
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


if __name__ == '__main__':
    args = get_args()
    Clutrr(args)

