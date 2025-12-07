import json
import os

MEMORY_FILE = "data/memory.json"

class Memory:
    def __init__(self):
        if not os.path.exists("data"):
            os.makedirs("data")

        if not os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "w") as f:
                json.dump([], f)

        with open(MEMORY_FILE, "r") as f:
            self.messages = json.load(f)

    def add(self, role, content):
        self.messages.append({"role": role, "content": content})
        with open(MEMORY_FILE, "w") as f:
            json.dump(self.messages, f, indent=4)

    def get(self):
        return self.messages

    def clear(self):
        self.messages = []
        with open(MEMORY_FILE, "w") as f:
            json.dump([], f, indent=4)

