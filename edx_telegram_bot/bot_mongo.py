from track.backends.mongodb import MongoBackend

class BotMongo(MongoBackend):

    def __init__(self, **kwargs):
        super(BotMongo, self).__init__(**kwargs)
        db_name = kwargs.get('database', 'track')
        self.database = self.connection[db_name]

    def find_one(self, query):
        return self.collection.find_one(query)

    def find_all(self):
        return self.collection.find()

    def get_all_courses(self):
        return self.database.collection_names()

    def check_index(self):
        return self.database.collection.index_information()

    def set_index(self, *args):
        return self.database.collection.create_index(*args)

    def upsert(self, document):
        print document
        self.collection.save(document)
