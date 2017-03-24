import praw

from r2d2_errors import R2D2_RedditError


class RedditWrapper:

    def __init__(self, configuration, subreddits):
        try:
            self.reddit = praw.Reddit(client_id = configuration["client_id"],
                                 client_secret = configuration["client_secret"],
                                 user_agent = configuration["user_agent"])

            # Parse the list of subreddits read from the config.
            multiple_subreddits=subreddits[0]
            for subreddit in subreddits[1:]:
                multiple_subreddits = multiple_subreddits + "+" + subreddit

            self.subreddits = self.reddit.subreddit(multiple_subreddits)

        except Exception as e:
            raise R2D2_RedditError(e.message)

    def getSubmissionsStream(self):
        return RedditWrapper.itemsStream(self.subreddits.stream.submissions,
                                 RedditWrapper.submissionToDict)

    def getCommentsStream(self):
        return RedditWrapper.itemsStream(self.subreddits.stream.comments,
                                 RedditWrapper.commentToDict)

    @staticmethod
    def itemsStream(itemsGenerator, normalizeItem):
        def stream():
            i = 1
            for item in itemsGenerator():
                if (i <= 100):
                    # First 100 items are historical.
                    # We discard them because we only want items starting from "now"
                    i += 1
                else:
                    yield normalizeItem(item)

        return stream

    @staticmethod
    def submissionToDict(submission):
        """Normalize the submissions into a simple dictionary format."""
        return RedditWrapper.createItem(submission.id,
                                        "SUBMISSION",
                                        submission.title,
                                        submission.created_utc,
                                        str(submission.subreddit))

    @staticmethod
    def commentToDict(comment):
        """Normalize the comments into a simple dictionary format."""
        return RedditWrapper.createItem(comment.id,
                                        "COMMENT",
                                        comment.body,
                                        comment.created_utc,
                                        str(comment.subreddit))

    @staticmethod
    def createItem(id, type, content, timestamp, subreddit):
        """Normalize DB items into a dictionary."""
        return {RedditWrapper.id_field:         id,
                RedditWrapper.type_field:       type,
                RedditWrapper.content_field:    content,
                RedditWrapper.timestamp_field:  timestamp,
                RedditWrapper.subreddit_field:  subreddit}

    # The names of the fields in the dictionary used to represent items
    # retrieved from the DB
    id_field = "reddit_id"
    type_field = "type"
    content_field = "content"
    timestamp_field = "timestamp"
    subreddit_field = "subreddit"