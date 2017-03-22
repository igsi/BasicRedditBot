from sources.reddit_api_wrapper import RedditWrapper
from sources.configuration import getConfiguration

from unittest import TestCase
import mock


class TestRedditWrapper(TestCase):
    """This class tests that the wrapper uses the praw api correctly.
    It is not meant to test praw itself."""

    def setUp(self):
        self.config = getConfiguration()

        self.submission = type('DummySubmission', (object,), { "id": "some_id",
                                                               "title": "some_title",
                                                               "created_utc": 1234,
                                                               "subreddit": "some_subreddit"})

        self.submissionExpected = {"reddit_id": self.submission.id,
                                   "type": "SUBMISSION",
                                   "content": self.submission.title,
                                   "timestamp": self.submission.created_utc,
                                   "subreddit": str(self.submission.subreddit)}

        self.comment = type('DummyComment', (object,), {"id": "some_id",
                                                        "body": "some_content",
                                                        "created_utc": 1234,
                                                        "subreddit": "some_subreddit"})

        self.commentExpected = {"reddit_id": self.comment.id,
                                "type": "COMMENT",
                                "content": self.comment.body,
                                "timestamp": self.comment.created_utc,
                                "subreddit": str(self.comment.subreddit)}

    @mock.patch.object(RedditWrapper, "_itemsStream")
    def test__itemsStream(self, mock_itemsStream):
        """Mocks calls to method _itemStream of the RedditWrapper class.
        Tests that it is called correctly when trying to retrieve comments/submissions."""
        reddit = RedditWrapper(self.config["reddit"], self.config["subreddits"])

        # Check that the submission stream is called correctly.
        reddit.getSubmissionsStream()
        reddit._itemsStream.assert_called_with(reddit.subreddits.stream.submissions,
                                               RedditWrapper._jsonifySubmission)

        # Check that the comments stream is called correctly.
        reddit.getCommentsStream()
        reddit._itemsStream.assert_called_with(reddit.subreddits.stream.comments,
                                               RedditWrapper._jsonifyComment)

    def test_jsonifySubmission(self):
        json_submission = RedditWrapper._jsonifySubmission(self.submission)

        self.assertDictEqual(json_submission, self.submissionExpected)

    def test_jsonifyComment(self):
        json_comment = RedditWrapper._jsonifyComment(self.comment)

        self.assertDictEqual(json_comment, self.commentExpected)

