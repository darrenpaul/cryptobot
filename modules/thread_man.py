__version__ = '0.0.1'


import threading


class ThreadManager:
    def __init__(self, auto_start=True):
        self.auto_start = auto_start
        self.threads = []
        self.data = []

    def spawn_new_thread(self, thread_name, function, **kwargs):
        t = ThreadInstance(thread_name, function, **kwargs)
        self.threads.append(t)
        if self.auto_start:
            t.start()

    def start_all_threads(self):
        if not self.threads:
            print("No threads to start")
            return False
        for t in self.threads:
            t.start()

    def join_threads(self):
        for t in self.threads:
            t.join()
            if isinstance(t.data, list):
                self.data = self.data = t.data
            else:
                self.data.append(t.data)


class ThreadInstance(threading.Thread):
    def __init__(self, name, function, **kwargs):
        threading.Thread.__init__(self)
        self.name = name
        self.function = function
        self.function_args = kwargs
        self.silent = False
        self.data = None

    def run(self):
        if not self.silent:
            print("starting " + self.name)
        self.data = self.function(**self.function_args)
        if not self.silent:
            print("finished {}".format(self.name))


def chunk_data(list_data, chunk):
    for i in range(0, len(list_data), chunk):
        yield list_data[i:i+chunk]
