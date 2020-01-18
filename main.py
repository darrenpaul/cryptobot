from modules import watcher
from modules import buyer


w = watcher.Watcher(dry_run=False)
w.start_watcher()

b = buyer.Buyer(dry_run=False)
b.start_buyer()

# START SELLER
# START BUYER
