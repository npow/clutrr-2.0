## Wrapper to communicate with backend database
## The database (Mongo) is used to maintain a set of collections
#### - data we need to annotate : gold
#### - dump for annotated data : mturk  - this should also contain our manual tests

from pymongo import MongoClient
import pandas as pd
import random

class DB:
    def __init__(self, host='localhost', port=27017, collection='amt_study', test_prob=0.2, test_worker='test'):
        # initiate the db connection
        self.client = MongoClient(host, port)
        print("Connected to backed MongoDB data at {}:{}".format(host, port))
        self.gold = self.client[collection]['gold']
        self.mturk = self.client[collection]['mturk']
        self.test_prob = test_prob
        self.test_worker = test_worker

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
        data = self._read_csv(data_path)
        records = data.to_dict(orient='records')
        # add used counter if gold and test
        # add reviewed counter if mturk
        for rec in records:
            if db == 'gold':
                rec['used'] = 0
            else:
                rec['reviewed'] = 0
        mdb = getattr(self, db)
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
        if random.uniform(0,1) <= self.test_prob:
            using_test = True
            record = self.mturk.find_one({'worker_id': self.test_worker}, sort=[("reviewed",1)])
        else:
            record = self.mturk.find_one({'worker_id': {"$ne": worker_id}}, sort=[("reviewed",1)])

        if not using_test and not record:
            # if no canidate peer is found, default to test
            record = self.mturk.find_one({'worker_id': self.test_worker}, sort=[("reviewed",1)])
        if record:
            self.mturk.update_one({'_id': record['_id']}, {'$inc': {'used': 1}}, upsert=False)
        else:
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
        record['reviews'] += record['reviews'] + rating
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

    def export(self):
        """
        Dump datasets into csv
        :return:
        """
        gold = pd.DataFrame(list(self.gold.find()))
        mturk = pd.DataFrame(list(self.mturk.find()))
        gold.to_csv("amt_gold.csv")
        mturk.to_csv("amt_mturk.csv")

if __name__ == '__main__':
    data = DB(port=8092)
    data.upload('/home/ml/ksinha4/mlp/clutrr/data/data_633c86c0/2.2_train.csv', db='gold')
    g = data.get_gold()
    print(g)
    g['paraphrase'] = 'This is a sample paraphrase'
    data.save_annotation(g, '123')
    g['paraphrase'] = 'This is a test paraphrase'
    data.save_annotation(g, 'test')
    p = data.get_peer(worker_id='1')
    data.save_review(p, '1', rating=1)
    assert len(p) == 1
