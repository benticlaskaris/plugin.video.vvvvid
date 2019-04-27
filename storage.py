from default import CWD
import os
import pickle


class Storage:
    FILENAME = os.path.join(CWD, "storage.pkl")

    def __init__(self):
        if os.path.exists(Storage.FILENAME):
            self.data = pickle.load(open(Storage.FILENAME, "rb"))
            if not self.data:
                self.data = {}
        else:
            self.data = {}

    def get(self, id):
        return self.data.get(id)

    def set(self, id, value):
        self.data[id] = value
        pickle.dump(self.data, open(Storage.FILENAME, "wb"))
