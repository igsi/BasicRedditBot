import signal
import sys
import threading
import time

import configuration
from db_api_wrapper import DBWrapper
from reddit_api_wrapper import RedditWrapper

stop_event = threading.Event()


def exitGracefully(signum, frame):
    print "Stopping everything, please wait..."
    stop_event.set()

    # Because waiting for a new item in monitorForNewEntriesAndSaveInDB is blocking,
    # until new items are inserted the stop_event will not be checked.
    # If 10 seconds elapse and the program is still running, we exit forcefully.
    time.sleep(10)
    print "Bye!"
    sys.exit()


def monitorForNewEntriesAndSaveInDB(stream, db, stop_event=None):
    for item in stream():
        if (stop_event is not None and stop_event.is_set()):
            break
        db.insert(item)


def monitorSubreddits():
    config = configuration.getConfiguration()
    reddit = RedditWrapper(config["reddit"], config["subreddits"])
    db = DBWrapper(config["database"])

    threadPost = threading.Thread(target=monitorForNewEntriesAndSaveInDB,
                                  args=(reddit.getCommentsStream(), db, stop_event))

    signal.signal(signal.SIGINT, exitGracefully)

    # Do work in other thread. Listen for new comments.
    threadPost.start()

    # Do work in main thread. Listen for new submissions
    monitorForNewEntriesAndSaveInDB(reddit.getSubmissionsStream(), db, stop_event)

    threadPost.join()

    print "Bye!"


if __name__ == '__main__':
    monitorSubreddits()
