import pymongo


# available fields: reddit_id, type, content, timestamp, subreddit

class DBWrapper:

    def __init__(self, configuration):
        self.mongo = pymongo.MongoClient(configuration["host"],
                                         configuration["port"])

        self.db = self.mongo["reddit_data"]

        if "items" not in self.db.collection_names():
            self.db.create_collection("items")

        self.items = self.db["items"]

        self._createIndexes()

    def insert(self, data):
        self.items.insert(data)

    def _createIndexes(self):
        indexName1 = "subredditIndex"
        indexName2 = "keywordIndex"

        if indexName1 not in self.items.index_information():
            self.items.create_index([("timestamp", pymongo.DESCENDING), ("subreddit", pymongo.ASCENDING)],
                                    name=indexName1)

        # This index will provide keyword search capabilities on the content field.
        if indexName2 not in self.items.index_information():
            self.items.create_index([("content", pymongo.TEXT)],
                                    default_language="none", # use simple tokenization and exact keyword match
                                    name=indexName2)
