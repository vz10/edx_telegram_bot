from track.backends.mongodb import MongoBackend

class BotMongo(MongoBackend):

    def __init__(self, **kwargs):
        super(BotMongo, self).__init__(**kwargs)

    def find(self, query):
        return self.collection.find(query)