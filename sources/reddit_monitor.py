import signal
import sys
import threading
import time

import configuration
from db_api_wrapper import DBWrapper
from reddit_api_wrapper import RedditWrapper
from r2d2_errors import R2D2_RedditError, R2D2_ConfigurationError, R2D2_DatabaseError


# This event is used to notify threads to stop listening for new items on the monitored subreddits.
stop_event = threading.Event()


def exitGracefully(signum, frame):
    """Handler for SIGINT. Used to terminate the program."""

    print "Stopping everything, please wait..."
    stop_event.set() # notify threads to stop, if they are not blocked

    # Because waiting for a new item in monitorForNewEntriesAndSaveInDB is blocking,
    # until new items are inserted the stop_event will not be checked.
    # If 10 seconds elapse and the program is still running, we exit forcefully.
    time.sleep(10)
    print "Bye!"
    sys.exit()


def monitorForNewEntriesAndSaveInDB(stream, db, stop_event=None):
    """Takes as input a generator (stream) and whenever a new item is generated it is saved in the db."""
    for item in stream():
        if (stop_event is not None and stop_event.is_set()):
            break
        db.insert(item)


def monitorSubreddits():
    """Listens for new entries (submissions and comments) in the monitored subreddits.
    The list of subredits to monitor is specified in configuration.json."""

    # Gets the configuration to use. These are settings regarding how to connect to
    # the DB and which subreddits to listen to.
    config = configuration.getConfiguration()

    print "Monitoring the following subreddits for new submissions/comments: " + str(config["subreddits"])

    # Object used to access the Reddit API.
    reddit = RedditWrapper(config["reddit"], config["subreddits"])
    db = DBWrapper(config["database"])

    # Create a new thread which will listen for new comments.
    threadPost = threading.Thread(target=monitorForNewEntriesAndSaveInDB,
                                  args=(reddit.getCommentsStream(), db, stop_event))

    # From this point on, change the handler used when the user send SIGINT.
    signal.signal(signal.SIGINT, exitGracefully)

    # Do work in the other thread. Listen for new comments.
    threadPost.start()

    # Do work in main thread. Listen for new submissions
    monitorForNewEntriesAndSaveInDB(reddit.getSubmissionsStream(), db, stop_event)

    threadPost.join()

    print "Bye!"


if __name__ == '__main__':
    try:
        monitorSubreddits()

    except R2D2_RedditError as e:
        print "An error occured when trying to connect to Reddit."
        print e.message
        sys.exit(2)

    except R2D2_ConfigurationError as e:
        print "An error occured when trying to read the configuration file 'Configuration.json'."
        print e.message
        sys.exit(3)

    except R2D2_DatabaseError as e:
        print "An error occured when trying to connect to the database."
        print e.message
        sys.exit(4)

    except Exception as e:
        print "An unexpected error ocured: ", e.message
        sys.exit(1)
