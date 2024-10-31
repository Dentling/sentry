import unittest
from unittest.mock import patch

from sentry.testutils.cases import TestCase
from sentry.utils.event_tracker import (
    EventType,
    TransactionStageStatus,
    should_track,
    track_sampled_event,
)

EVENT_ID = "9cdc4c32dff14fbbb012b0aa9e908126"
EVENT_TYPE_STR = "transaction"
STATUS = TransactionStageStatus.REDIS_PUT

EXPECTED_EVENT_TYPE = EventType.TRANSACTION


class TestEventTracking(TestCase):

    @patch("sentry.utils.event_tracker._do_record")
    def test_track_sampled_event_logs_event(self, mock_do_record):
        with patch("sentry.utils.event_tracker.should_track", return_value=True):
            track_sampled_event(EVENT_ID, EVENT_TYPE_STR, STATUS)
            mock_do_record.assert_called_once_with(
                {"event_id": EVENT_ID, "event_type": EXPECTED_EVENT_TYPE, "status": STATUS}
            )

    @patch("sentry.utils.event_tracker._do_record")
    def test_track_sampled_event_does_not_log_event(self, mock_do_record):
        with patch("sentry.utils.event_tracker.should_track", return_value=False):
            track_sampled_event(EVENT_ID, EVENT_TYPE_STR, STATUS)
            mock_do_record.assert_not_called()

    def test_should_track_true(self):
        result = should_track(EVENT_ID, 1)
        self.assertTrue(result)

    def test_should_track_false(self):
        # Test should_track returns False for 0 rate
        result = should_track(EVENT_ID, 0)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
