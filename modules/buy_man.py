import thread_man
import collector
import time


class Buyer:
    def __init__(self):
        self.intervals = 60
        self.last_price = 8800.00

    def start_buyer(self):
        while True:
            print(collector.latest_ticker('btceur'))
            time.sleep(self.intervals)


w = Watcher()
w.start_buyer()
