from modules import watcher
from modules import buyer


w = watcher.Watcher(dry_run=True)
w.start_watcher()

b = buyer.Buyer(dry_run=True)
b.start_buyer()

# START SELLER
# START BUYER
