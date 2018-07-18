import time


class Timer:

    def __init__(self):
        self.start_time = 0
        self.end_time = 0
        self.time_diff = 0

    def reset(self):
        self.start_time = 0
        self.end_time = 0
        self.time_diff = 0

    def start(self):
        self.start_time = time.time()

    def end(self):
        self.end_time = time.time()
        self.time_diff = self.end_time - self.start_time
        return self.time_diff

    def get(self):
        return self.time_diff
