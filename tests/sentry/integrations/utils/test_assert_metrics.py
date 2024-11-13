from sentry.integrations.types import EventLifecycleOutcome

"""
Helper functions to assert integration SLO metrics
"""


def assert_halt_metric(mock_record, error_msg):
    (event_failures,) = (
        call for call in mock_record.mock_calls if call.args[0] == EventLifecycleOutcome.HALTED
    )
    # TODO: enforce "halt_reason" in the metric
    assert event_failures.args[1]["halt_reason"] == error_msg


def assert_failure_metric(mock_record, error_msg):
    (event_failures,) = (
        call for call in mock_record.mock_calls if call.args[0] == EventLifecycleOutcome.FAILURE
    )
    # TODO: enforce "failure_reason" in the metric
    assert event_failures.args[1]["failure_reason"] == error_msg
