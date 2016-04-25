"""
Various implementations of a queue
"""

class Queue:
    filename = None

    """An in-memory FIFO that syncs to disk"""
    def push(self, message):
        """Push a message onto the queue"""

    def pop(self):
        """Pop a message off the queue"""

    def sync(self):
        """Sync the queue to disk"""
