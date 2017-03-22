import pymongo


# available fields: reddit_id, type, content, timestamp, subreddit

class DBWrapper:

    def __init__(self, configuration):
        try:
            self.mongo = pymongo.MongoClient(configuration["host"],
                                             configuration["port"])

            self.db = self.mongo["reddit_data"]

            # If this collection does not exist, force its creation. This is required in order to create the indexes.
            if "items" not in self.db.collection_names():
                self.db.create_collection("items")
            self.items = self.db["items"]

            self._createIndexes()
        except:
            print "Could not create DB connection"
            raise

    def insert(self, data):
        self.items.insert(data)

    def _createIndexes(self):
        """Checks to see if indexes exist. If not it creates them."""
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
