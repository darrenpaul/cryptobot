__version__ = '0.0.1'


import pymongo
from . import setup


class Mongo:
    def __init__(self, database_name, database_collection):
        self.client = pymongo.MongoClient(
            setup.DATABASE_IP,
            setup.DATABASE_PORT,
            # ssl=True,
            # ssl_certfile=setup.SSL_CERTFILE,
            # ssl_ca_certs=setup.SSL_CA_CERTS)
        )
        self.database = self.client[database_name]
        self.collection = self.database[database_collection]

    def create_database(self):
        pass

    def create_collection(self):
        pass

    def get_entire_collection(self):
        return self.collection.find()

    def query_database(self, query):
        query_result = self.collection.find(query)
        for i in query_result:
            return i
        return None

    def add_single(self, dict_data):
        return self.collection.insert_one(dict_data).inserted_id

    def add_many(self, list_data):
        if not list_data:
            return
        for i in chunk_data(list_data=list_data, chunk_size=setup.DATABASE_CHUNK):
            result = self.collection.insert_many(i)
        return result

    def update_many(self, list_data, query_key):
        if not list_data:
            return
        for i in list_data:
            query = {query_key: str(i[query_key])}
            updates = {'$set': i}
            return self.collection.update_many(query, updates)

    def delete_single(self, query):
        result = self.collection.delete_one(query)
        print(result.deleted_count)

    def delete_many(self, query):
        result = self.collection.delete_many(query)
        print(result.deleted_count)

    def drop_collection(self, collection_name):
        self.database.drop_collection(collection_name)
        print('deleted ' + collection_name)


def chunk_data(list_data, chunk):
    for i in range(0, len(list_data), chunk):
        yield list_data[i:i+chunk]
