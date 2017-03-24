from sources.reddit_api_wrapper import RedditWrapper
from sources.configuration import getConfiguration

from unittest import TestCase
import mock


class TestRedditWrapper(TestCase):
    """This class tests that the wrapper uses the praw api correctly.
    It is not meant to test praw itself."""

    def setUp(self):
        self.config = getConfiguration()

        self.submission = type('DummySubmission', (object,), { "id":            "some_id",
                                                               "title":         "some_title",
                                                               "created_utc":   1234,
                                                               "subreddit":     "some_subreddit"})

        self.submissionExpected = {RedditWrapper.id_field:          self.submission.id,
                                   RedditWrapper.type_field:        "SUBMISSION",
                                   RedditWrapper.content_field:     self.submission.title,
                                   RedditWrapper.timestamp_field:   self.submission.created_utc,
                                   RedditWrapper.subreddit_field:   str(self.submission.subreddit)}

        self.comment = type('DummyComment', (object,), {"id":           "some_id",
                                                        "body":         "some_content",
                                                        "created_utc":  1234,
                                                        "subreddit":    "some_subreddit"})

        self.commentExpected = {RedditWrapper.id_field:         self.comment.id,
                                RedditWrapper.type_field:       "COMMENT",
                                RedditWrapper.content_field:    self.comment.body,
                                RedditWrapper.timestamp_field:  self.comment.created_utc,
                                RedditWrapper.subreddit_field:  str(self.comment.subreddit)}


    @mock.patch.object(RedditWrapper, "itemsStream")
    def test_getSubmissionsStream(self, mock_itemsStream):
        """Mock calls to method _itemStream.
        Test that it is called correctly when trying to retrieve submissions."""
        reddit = RedditWrapper(self.config["reddit"], self.config["subreddits"])

        # Check that the submission stream is called correctly.
        reddit.getSubmissionsStream()
        reddit.itemsStream.assert_called_with(reddit.subreddits.stream.submissions,
                                               RedditWrapper.submissionToDict)

    @mock.patch.object(RedditWrapper, "itemsStream")
    def test_getCommentsStream(self, mock_itemsStream):
        """Mock calls to method _itemStream.
        Test that it is called correctly when trying to retrieve submissions."""
        reddit = RedditWrapper(self.config["reddit"], self.config["subreddits"])

        # Check that the comments stream is called correctly.
        reddit.getCommentsStream()
        reddit.itemsStream.assert_called_with(reddit.subreddits.stream.comments,
                                               RedditWrapper.commentToDict)

    def test_itemsStream(self):
        """ Test that the first 100 items retrieved by the items generator are discarded. """
        items = []
        for i in range(0, 100):
            items.append(self.helper_createDbSubmission("TO_BE_DISCARDED", "", 0, ""))
        items.append(self.helper_createDbSubmission("FIRST VALUE RETURNED", "", 0, ""))
        items.append(self.helper_createDbSubmission("SECOND VALUE RETURNED", "", 0, ""))

        mock_itemsGenerator = mock.MagicMock()
        mock_itemsGenerator.return_value = iter(items)

        generator = RedditWrapper.itemsStream(mock_itemsGenerator, RedditWrapper.submissionToDict)

        returned_items = list(generator())

        self.assertEqual(returned_items[0][RedditWrapper.id_field], "FIRST VALUE RETURNED")
        self.assertEqual(returned_items[1][RedditWrapper.id_field], "SECOND VALUE RETURNED")

    def test_submissionToDict(self):
        submission = RedditWrapper.submissionToDict(self.submission)

        self.assertDictEqual(submission, self.submissionExpected)

    def test_commentToDict(self):
        comment = RedditWrapper.commentToDict(self.comment)

        self.assertDictEqual(comment, self.commentExpected)

    @staticmethod
    def helper_createDbSubmission(id, title, time, subreddit):
        return type('DummySubmission', (object,), {"id":            id,
                                                   "title":         title,
                                                   "created_utc":   time,
                                                   "subreddit":     subreddit})