## Wrapper to communicate with backend database
## The database (Mongo) is used to maintain a set of collections
#### - data we need to annotate : gold
#### - dump for annotated data : mturk
#### - dump for manual test conditions : test

from pymongo import MongoClient
import pandas as pd

class DB:
    def __init__(self, host='localhost', port=27017, collection='amt_study'):
        # initiate the db connection
        self.client = MongoClient(host, port)
        print("Connected to backed MongoDB data at {}:{}".format(host, port))
        self.gold = self.client[collection]['gold']
        self.mturk = self.client[collection]['mturk']
        self.test = self.client[collection]['test']

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
            if db == 'gold' or db == 'test':
                rec['used'] = 0
            else:
                rec['reviewed'] = 0
        mdb = getattr(self, db)
        r = mdb.insert_many(records)
        print("Inserted {} records in db {}".format(len(records), db))

    def get_gold(self):
        record = self.gold.find_one(sort=[("used",1)])
        # update counter
        self.gold.update_one({'_id': record['_id']}, {'$inc': {'used': 1}}, upsert=False)
        return record

    def get_test(self):
        record = self.test.find_one(sort=[("used", 1)])
        # update counter
        self.test.update_one({'_id': record['_id']}, {'$inc': {'used': 1}}, upsert=False)
        return record

    def get_peer(self):
        record = self.mturk.find_one(sort=[("reviewed",1)])
        self.mturk.update_one({'_id': record['_id']}, {'$inc': {'used': 1}}, upsert=False)
        return record

    def save_review(self, record, rating=0.0):
        """
        Save the review. If its correct, then 1.0, else 0.0.
        :param record:
        :param rating:
        :return:
        """
        record['reviews'] += record['reviews'] + rating
        self.mturk.update_one({'_id': record['_id']}, {"$set": record}, upsert=False)

    def save_annotation(self, record):
        self.mturk.insert_one(record)

    def export(self):
        """
        Dump datasets into csv
        :return:
        """
        gold = pd.DataFrame(list(self.gold.find()))
        mturk = pd.DataFrame(list(self.mturk.find()))
        test = pd.DataFrame(list(self.test.find()))
        gold.to_csv("amt_gold.csv")
        mturk.to_csv("amt_mturk.csv")
        test.to_csv("amt_test.csv")

if __name__ == '__main__':
    data = DB(port=8092)
    data.upload('data/data_633c86c0/2.2_train.csv', db='gold')
    data.upload('data/data_633c86c0/1.2_test.csv', db='test')
    g = data.get_gold()
    print(g)
    g['paraphrase'] = 'This is a sample paraphrase'
    data.save_annotation(g)
    print(data.get_peer())
    data.export()
