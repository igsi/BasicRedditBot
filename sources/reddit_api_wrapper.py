import praw


class RedditWrapper:

    def __init__(self, configuration, subreddits):
        self.reddit = praw.Reddit(client_id = configuration["client_id"],
                             client_secret = configuration["client_secret"],
                             user_agent = configuration["user_agent"])

        # Parse the list of subreddits read from the config.
        multiple_subreddits=subreddits[0]
        for subreddit in subreddits[1:]:
            multiple_subreddits = multiple_subreddits + "+" + subreddit

        self.subreddits = self.reddit.subreddit(multiple_subreddits)

    def getSubmissionsStream(self):
        return self._itemsStream(self.subreddits.stream.submissions,
                                 self._jsonifySubmission)

    def getCommentsStream(self):
        return self._itemsStream(self.subreddits.stream.comments,
                                 self._jsonifyComment)

    def _itemsStream(self, itemsGenerator, jsonifyItem):
        def stream():
            i = 1
            for item in itemsGenerator():
                if (i <= 100):
                    # first 100 items are historical
                    # we discard them because we only want items starting from now
                    i += 1
                else:
                    yield jsonifyItem(item)

        return stream

    def _jsonifySubmission(self, submission):
        """Normalize the submissions into a simple json format."""
        return {"reddit_id": submission.id,
                "type": "SUBMISSION",
                "content": submission.title,
                "timestamp": submission.created_utc,
                "subreddit": str(submission.subreddit)}

    def _jsonifyComment(self, comment):
        """Normalize the comments into a simple json format."""
        return {"reddit_id": comment.id,
                "type": "COMMENT",
                "content": comment.body,
                "timestamp": comment.created_utc,
                "subreddit": str(comment.subreddit)}