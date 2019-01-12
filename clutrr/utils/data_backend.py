## Wrapper to communicate with backend database
## The database (Mongo) is used to maintain a set of collections
#### - data we need to annotate : gold
#### - dump for annotated data : mturk  - this should also contain our manual tests

from pymongo import MongoClient
import pandas as pd
import random
import glob
import schedule
import time
import datetime
import pdb

KOUSTUV_ID = "A1W0QQF93UM08"

class DB:
    def __init__(self, host='localhost', port=27017, collection='amt_study', test_prob=0.2):
        # initiate the db connection
        self.client = MongoClient(host, port)
        #print("Connected to backend MongoDB data at {}:{}".format(host, port))
        self.gold = self.client[collection]['gold']
        self.mturk = self.client[collection]['mturk']
        self.test_prob = test_prob
        self.test_worker = KOUSTUV_ID

    def _read_csv(self, path):
        assert path.endswith('.csv')
        return pd.read_csv(path)

    def upload(self, data_path, db='gold'):
        """
        Given a csv file, upload the entire dataframe in the particular db
        :param data:
        :param db:
        :return:
        """
        print("Reading {}".format(data_path))
        data = self._read_csv(data_path)
        records = data.to_dict(orient='records')
        # add used counter if gold and test
        # add reviewed counter if mturk
        num_records = len(records)
        print("Number of records found : {}".format(len(records)))
        for rec in records:
            if db == 'gold':
                rec['used'] = 0
            else:
                rec['reviewed'] = 0
        mdb = getattr(self, db)
        # prune the records which are already present in the database
        keep_idx = []
        for rec_idx, rec in enumerate(records):
            fd = mdb.find({'id': rec['id']}).count()
            if fd == 0:
                keep_idx.append(rec_idx)
        records = [records[idx] for idx in keep_idx]
        num_kept = len(records)
        print("Number of records already in db : {}".format(num_records - num_kept))
        if len(records) > 0:
            r = mdb.insert_many(records)
        print("Inserted {} records in db {}".format(len(records), db))

    def get_gold(self):
        record = self.gold.find_one(sort=[("used",1)])
        # update counter
        if record:
            self.gold.update_one({'_id': record['_id']}, {'$inc': {'used': 1}}, upsert=False)
        return record

    def get_peer(self, worker_id='test'):
        """
        Get an annotation which is not done by the current worker, and which isn't reviewed
        With some probability, choose our test records
        TODO: it would be nice if we can avoid the annotations done by the same worker here
        :param worker_id:
        :return: None if no suitable candidate found
        """
        using_test = False
        record = None
        if random.uniform(0,1) <= self.test_prob:
            using_test = True
            record_cursor = self.mturk.find({'worker_id': self.test_worker}, sort=[("used",1)])
        else:
            record_cursor = self.mturk.find({'worker_id': {"$ne": worker_id}}, sort=[("used",1)])
        rec_found = False
        if record_cursor.count() > 0:
            rec_found = True
        if not using_test and not rec_found:
            # if no candidate peer is found, default to test
            record_cursor = self.mturk.find({'worker_id': self.test_worker},
                    sort=[("used",1)])
        if record_cursor.count() > 0:
            record = list(record_cursor)[0]
        if not record:
            # did not find either candidate peer nor test, raise error
            raise FileNotFoundError("no candidate found in db")
        return record

    def save_review(self, record, worker_id, rating=0.0):
        """
        Save the review. If its correct, then 1.0, else 0.0.
        :param record:
        :param rating:
        :return:
        """
        assert 'reviews' in record
        assert 'reviewed_by' in record
        record['used'] = len(record['reviewed_by']) + 1
        record['reviewed_by'].append({worker_id: rating})
        self.mturk.update_one({'_id': record['_id']}, {"$set": record}, upsert=False)

    def save_annotation(self, record, worker_id):
        if 'worker_id' not in record:
            record['worker_id'] = ''
        record['worker_id'] = worker_id
        if 'reviews' not in record:
            record['reviews'] = 0
        record['reviews'] = 0
        if 'reviewed_by' not in record:
            record['reviewed_by'] = []
        record['reviewed_by'] = []
        # change the id
        record['gold_id'] = record['_id']
        del record['_id']
        self.mturk.insert_one(record)

    def import_data(self):
        path = '/home/ml/ksinha4/mlp/clutrr/mturk_data/*'
        print("Checking the path: {}".format(path))
        files = glob.glob(path)
        print("Files found : {}".format(len(files)))
        for fl in files:
            if fl.endswith('gold.csv'):
                self.upload(fl, db='gold')
            if fl.endswith('mturk.csv'):
                self.upload(fl, db='mturk')

    def export(self, base_path='/home/ml/ksinha4/mlp/clutrr/mturk_data/'):
        """
        Dump datasets into csv
        :return:
        """
        gold = pd.DataFrame(list(self.gold.find()))
        mturk = pd.DataFrame(list(self.mturk.find()))
        gold.to_csv(base_path + "amt_gold.csv")
        mturk.to_csv(base_path + "amt_mturk.csv")

    def close_connections(self):
        #print("Closing connection")
        self.client.close()


def import_job():
    data = DB(port=8092)
    data.import_data()
    data.close_connections()

def export_job():
    data = DB(port=8092)
    data.export()
    data.close_connections()

def backup_job():
    data = DB(port=8092)
    data.export(base_path='/home/ml/ksinha4/datasets/clutrr_mturk/')
    data.export(base_path='/mnt/hdd/datasets/clutrr_mturk/')
    data.close_connections()

def info_job():
    data = DB(port=8092)
    print("Generating statistics at {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    gold_c = data.gold.find({}).count()
    pending_c = data.gold.find({'used':0}).count()
    avg_used = list(data.gold.aggregate([{'$group': {'_id':None,'avg' : {'$avg' : '$used'}}}]))
    if len(avg_used) > 0:
        avg_used = avg_used[0]['avg']
    mturk_c = data.mturk.find({}).count()
    uniq_workers = len(data.mturk.find({}).distinct("worker_id"))
    print("Number of gold data : {} \n ".format(gold_c) +
          "Number of pending rows to annotate : {} \n ".format(pending_c) +
          "Average times each gold row has been used : {} \n ".format(avg_used) +
          "Number of annotations given : {} \n".format(mturk_c) +
          "Unique workers : {}".format(uniq_workers))



if __name__ == '__main__':
    print("Scheduling jobs...")
    schedule.every(1).minutes.do(import_job)
    schedule.every(10).minutes.do(export_job)
    schedule.every(1).minutes.do(info_job)
    # redundant backup
    schedule.every().day.at("23:00").do(backup_job)

    while True:
        schedule.run_pending()
        time.sleep(1)
