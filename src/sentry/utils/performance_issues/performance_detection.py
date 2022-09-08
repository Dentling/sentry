import hashlib
import logging
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Union

import sentry_sdk

from sentry import options, projectoptions
from sentry.eventstore.models import Event
from sentry.models import ProjectOption
from sentry.types.issues import GroupType
from sentry.utils import metrics

from .performance_span_issue import PerformanceSpanProblem

Span = Dict[str, Any]
TransactionSpans = List[Span]
PerformanceProblemsMap = Dict[str, PerformanceSpanProblem]

PERFORMANCE_GROUP_COUNT_LIMIT = 10


class DetectorType(Enum):
    SLOW_SPAN = "slow_span"
    DUPLICATE_SPANS_HASH = "dupes_hash"  # Have to stay within tag key length limits
    DUPLICATE_SPANS = "duplicates"
    SEQUENTIAL_SLOW_SPANS = "sequential"
    LONG_TASK_SPANS = "long_task"
    RENDER_BLOCKING_ASSET_SPAN = "render_blocking_assets"
    N_PLUS_ONE_SPANS = "n_plus_one"
    N_PLUS_ONE_DB_QUERIES = "n_plus_one_db"


DETECTOR_TYPE_TO_GROUP_TYPE = {
    DetectorType.SLOW_SPAN: GroupType.PERFORMANCE_SLOW_SPAN,
    # both duplicate spans hash and duplicate spans are mapped to the same group type
    DetectorType.DUPLICATE_SPANS_HASH: GroupType.PERFORMANCE_DUPLICATE_SPANS,
    DetectorType.DUPLICATE_SPANS: GroupType.PERFORMANCE_DUPLICATE_SPANS,
    DetectorType.SEQUENTIAL_SLOW_SPANS: GroupType.PERFORMANCE_SEQUENTIAL_SLOW_SPANS,
    DetectorType.LONG_TASK_SPANS: GroupType.PERFORMANCE_LONG_TASK_SPANS,
    DetectorType.RENDER_BLOCKING_ASSET_SPAN: GroupType.PERFORMANCE_RENDER_BLOCKING_ASSET_SPAN,
    DetectorType.N_PLUS_ONE_SPANS: GroupType.PERFORMANCE_N_PLUS_ONE,
    DetectorType.N_PLUS_ONE_DB_QUERIES: GroupType.PERFORMANCE_N_PLUS_ONE_DB_QUERIES,
}


@dataclass
class PerformanceProblem:
    fingerprint: str
    op: str
    desc: str
    type: GroupType
    spans_involved: Sequence[str]


# Facade in front of performance detection to limit impact of detection on our events ingestion
def detect_performance_problems(data: Event) -> List[PerformanceProblem]:
    try:
        rate = options.get(
            "store.use-ingest-performance-detection-only"
        )  # TODO: Remove this option once performance.issues option is working.
        inner_rate = options.get("performance.issues.all.problem-detection")
        if rate and rate > random.random() and inner_rate and inner_rate > random.random():
            # Add an experimental tag to be able to find these spans in production while developing. Should be removed later.
            sentry_sdk.set_tag("_did_analyze_performance_issue", "true")
            with metrics.timer(
                "performance.detect_performance_issue", sample_rate=0.01
            ), sentry_sdk.start_span(
                op="py.detect_performance_issue", description="none"
            ) as sdk_span:
                return _detect_performance_problems(data, sdk_span)
    except Exception:
        logging.exception("Failed to detect performance problems")
    return []


# Gets some of the thresholds to perform performance detection. Can be made configurable later.
# Thresholds are in milliseconds.
# Allowed span ops are allowed span prefixes. (eg. 'http' would work for a span with 'http.client' as its op)
def get_detection_settings(project_id: str):
    default_settings = projectoptions.get_well_known_default(
        "sentry:performance_issue_settings",
        project=project_id,
    )
    issue_settings = ProjectOption.objects.get_value(
        project_id, "sentry:performance_issue_settings", default_settings
    )
    settings = {
        **default_settings,
        **issue_settings,
    }  # Merge saved settings into default so updating the default works in the future.

    return {
        DetectorType.DUPLICATE_SPANS: [
            {
                "count": 5,
                "cumulative_duration": 500.0,  # ms
                "allowed_span_ops": ["db", "http"],
            }
        ],
        DetectorType.DUPLICATE_SPANS_HASH: [
            {
                "count": 5,
                "cumulative_duration": 500.0,  # ms
                "allowed_span_ops": ["http"],
            },
        ],
        DetectorType.SEQUENTIAL_SLOW_SPANS: [
            {
                "count": 3,
                "cumulative_duration": 1200.0,  # ms
                "allowed_span_ops": ["db", "http", "ui"],
            }
        ],
        DetectorType.SLOW_SPAN: [
            {
                "duration_threshold": 1000.0,  # ms
                "allowed_span_ops": ["db"],
            },
            {
                "duration_threshold": 2000.0,  # ms
                "allowed_span_ops": ["http"],
            },
        ],
        DetectorType.LONG_TASK_SPANS: [
            {
                "cumulative_duration": 500.0,  # ms
                "allowed_span_ops": ["ui.long-task", "ui.sentry.long-task"],
            }
        ],
        DetectorType.RENDER_BLOCKING_ASSET_SPAN: {
            "fcp_minimum_threshold": 2000.0,  # ms
            "fcp_maximum_threshold": 10000.0,  # ms
            "fcp_ratio_threshold": 0.25,
            "allowed_span_ops": ["resource.link", "resource.script"],
        },
        DetectorType.N_PLUS_ONE_SPANS: [
            {
                "count": 3,
                "start_time_threshold": 5.0,  # ms
                "allowed_span_ops": ["http.client"],
            }
        ],
        DetectorType.N_PLUS_ONE_DB_QUERIES: {
            "count": settings["n_plus_one_db_count"],
            "duration_threshold": settings["n_plus_one_db_duration_threshold"],  # ms
        },
    }


def _detect_performance_problems(data: Event, sdk_span: Any) -> List[PerformanceProblem]:
    event_id = data.get("event_id", None)
    spans = data.get("spans", [])
    project_id = data.get("project")

    detection_settings = get_detection_settings(project_id)
    detectors = {
        DetectorType.DUPLICATE_SPANS: DuplicateSpanDetector(detection_settings, data),
        DetectorType.DUPLICATE_SPANS_HASH: DuplicateSpanHashDetector(detection_settings, data),
        DetectorType.SLOW_SPAN: SlowSpanDetector(detection_settings, data),
        DetectorType.SEQUENTIAL_SLOW_SPANS: SequentialSlowSpanDetector(detection_settings, data),
        DetectorType.LONG_TASK_SPANS: LongTaskSpanDetector(detection_settings, data),
        DetectorType.RENDER_BLOCKING_ASSET_SPAN: RenderBlockingAssetSpanDetector(
            detection_settings, data
        ),
        DetectorType.N_PLUS_ONE_SPANS: NPlusOneSpanDetector(detection_settings, data),
        DetectorType.N_PLUS_ONE_DB_QUERIES: NPlusOneDBSpanDetector(detection_settings, data),
    }

    # Create performance issues for N+1 DB queries first
    used_perf_issue_detectors = {DetectorType.N_PLUS_ONE_DB_QUERIES}

    for span in spans:
        for _, detector in detectors.items():
            detector.visit_span(span)
    for _, detector in detectors.items():
        detector.on_complete()

    report_metrics_for_detectors(event_id, detectors, sdk_span)

    detected_problems = [
        (i, detector_type)
        for detector_type in used_perf_issue_detectors
        for _, i in detectors[detector_type].stored_problems.items()
    ]

    truncated_problems = detected_problems[:PERFORMANCE_GROUP_COUNT_LIMIT]

    return [
        prepare_problem_for_grouping(problem, data, detector_type)
        for problem, detector_type in truncated_problems
    ]


def prepare_problem_for_grouping(
    problem: Union[PerformanceProblem, PerformanceSpanProblem],
    data: Event,
    detector_type: DetectorType,
) -> PerformanceProblem:
    # Don't transform if the caller has already done the work for us.
    # (TBD: All detectors should get updated to just return PerformanceProblem directly)
    if isinstance(problem, PerformanceProblem):
        return problem

    transaction_name = data.get("transaction")
    spans_involved = problem.spans_involved
    first_span_id = spans_involved[0]
    spans = data.get("spans", [])
    first_span = next((span for span in spans if span["span_id"] == first_span_id), None)
    op = first_span["op"]
    hash = first_span["hash"]
    desc = first_span["description"]

    group_type = DETECTOR_TYPE_TO_GROUP_TYPE[detector_type]
    group_fingerprint = fingerprint_group(transaction_name, op, hash, group_type)

    prepared_problem = PerformanceProblem(
        fingerprint=group_fingerprint,
        op=op,
        desc=desc,
        type=group_type,
        spans_involved=spans_involved,
    )

    return prepared_problem


def fingerprint_group(transaction_name, span_op, hash, problem_class):
    signature = (str(transaction_name) + str(span_op) + str(hash)).encode("utf-8")
    full_fingerprint = hashlib.sha1(signature).hexdigest()
    return f"1-{problem_class}-{full_fingerprint}"


# Creates a stable fingerprint given the same span details using sha1.
def fingerprint_span(span: Span):
    op = span.get("op", None)
    description = span.get("description", None)
    if not description or not op:
        return None

    signature = (str(op) + str(description)).encode("utf-8")
    full_fingerprint = hashlib.sha1(signature).hexdigest()
    fingerprint = full_fingerprint[
        :20
    ]  # 80 bits. Not a cryptographic usage, we don't need all of the sha1 for collision detection

    return fingerprint


# Simple fingerprint for broader checks, using the span op.
def fingerprint_span_op(span: Span):
    op = span.get("op", None)
    if not op:
        return None
    return op


def get_span_duration(span: Span):
    return timedelta(seconds=span.get("timestamp", 0)) - timedelta(
        seconds=span.get("start_timestamp", 0)
    )


class PerformanceDetector(ABC):
    """
    Classes of this type have their visit functions called as the event is walked once and will store a performance issue if one is detected.
    """

    def __init__(self, settings: Dict[str, Any], event: Event):
        self.settings = settings[self.settings_key]
        self._event = event
        self.init()

    @abstractmethod
    def init(self):
        raise NotImplementedError

    def find_span_prefix(self, settings, span_op: str):
        allowed_span_ops = settings.get("allowed_span_ops", [])
        if len(allowed_span_ops) <= 0:
            return True
        return next((op for op in allowed_span_ops if span_op.startswith(op)), False)

    def settings_for_span(self, span: Span):
        op = span.get("op", None)
        span_id = span.get("span_id", None)
        if not op or not span_id:
            return None

        span_duration = get_span_duration(span)
        for setting in self.settings:
            op_prefix = self.find_span_prefix(setting, op)
            if op_prefix:
                return op, span_id, op_prefix, span_duration, setting
        return None

    def event(self) -> Event:
        return self._event

    @property
    @abstractmethod
    def settings_key(self) -> DetectorType:
        raise NotImplementedError

    @abstractmethod
    def visit_span(self, span: Span) -> None:
        raise NotImplementedError

    def on_complete(self) -> None:
        pass

    @property
    @abstractmethod
    def stored_problems(self) -> PerformanceProblemsMap:
        raise NotImplementedError


class DuplicateSpanDetector(PerformanceDetector):
    """
    Broadly check for duplicate spans.
    """

    __slots__ = ("cumulative_durations", "duplicate_spans_involved", "stored_problems")

    settings_key = DetectorType.DUPLICATE_SPANS

    def init(self):
        self.cumulative_durations = {}
        self.duplicate_spans_involved = {}
        self.stored_problems = {}

    def visit_span(self, span: Span):
        settings_for_span = self.settings_for_span(span)
        if not settings_for_span:
            return
        op, span_id, op_prefix, span_duration, settings = settings_for_span
        duplicate_count_threshold = settings.get("count")
        duplicate_duration_threshold = settings.get("cumulative_duration")

        fingerprint = fingerprint_span(span)
        if not fingerprint:
            return

        self.cumulative_durations[fingerprint] = (
            self.cumulative_durations.get(fingerprint, timedelta(0)) + span_duration
        )

        if fingerprint not in self.duplicate_spans_involved:
            self.duplicate_spans_involved[fingerprint] = []

        self.duplicate_spans_involved[fingerprint] += [span_id]
        duplicate_spans_counts = len(self.duplicate_spans_involved[fingerprint])

        if not self.stored_problems.get(fingerprint, False):
            if duplicate_spans_counts >= duplicate_count_threshold and self.cumulative_durations[
                fingerprint
            ] >= timedelta(milliseconds=duplicate_duration_threshold):
                spans_involved = self.duplicate_spans_involved[fingerprint]
                self.stored_problems[fingerprint] = PerformanceSpanProblem(
                    span_id, op_prefix, spans_involved
                )


class DuplicateSpanHashDetector(PerformanceDetector):
    """
    Broadly check for duplicate spans.
    Uses the span grouping strategy hash to potentially detect duplicate spans more accurately.
    """

    __slots__ = ("cumulative_durations", "duplicate_spans_involved", "stored_problems")

    settings_key = DetectorType.DUPLICATE_SPANS_HASH

    def init(self):
        self.cumulative_durations = {}
        self.duplicate_spans_involved = {}
        self.stored_problems = {}

    def visit_span(self, span: Span):
        settings_for_span = self.settings_for_span(span)
        if not settings_for_span:
            return
        op, span_id, op_prefix, span_duration, settings = settings_for_span
        duplicate_count_threshold = settings.get("count")
        duplicate_duration_threshold = settings.get("cumulative_duration")

        hash = span.get("hash", None)
        if not hash:
            return

        self.cumulative_durations[hash] = (
            self.cumulative_durations.get(hash, timedelta(0)) + span_duration
        )

        if hash not in self.duplicate_spans_involved:
            self.duplicate_spans_involved[hash] = []

        self.duplicate_spans_involved[hash] += [span_id]
        duplicate_spans_counts = len(self.duplicate_spans_involved[hash])

        if not self.stored_problems.get(hash, False):
            if duplicate_spans_counts >= duplicate_count_threshold and self.cumulative_durations[
                hash
            ] >= timedelta(milliseconds=duplicate_duration_threshold):
                spans_involved = self.duplicate_spans_involved[hash]
                self.stored_problems[hash] = PerformanceSpanProblem(
                    span_id, op_prefix, spans_involved, hash
                )


class SlowSpanDetector(PerformanceDetector):
    """
    Check for slow spans in a certain type of span.op (eg. slow db spans)
    """

    __slots__ = "stored_problems"

    settings_key = DetectorType.SLOW_SPAN

    def init(self):
        self.stored_problems = {}

    def visit_span(self, span: Span):
        settings_for_span = self.settings_for_span(span)
        if not settings_for_span:
            return
        op, span_id, op_prefix, span_duration, settings = settings_for_span
        duration_threshold = settings.get("duration_threshold")

        fingerprint = fingerprint_span(span)

        if not fingerprint:
            return

        if span_duration >= timedelta(
            milliseconds=duration_threshold
        ) and not self.stored_problems.get(fingerprint, False):
            spans_involved = [span_id]
            self.stored_problems[fingerprint] = PerformanceSpanProblem(
                span_id, op_prefix, spans_involved
            )


class SequentialSlowSpanDetector(PerformanceDetector):
    """
    Checks for unparallelized slower repeated spans, to suggest using futures etc. to reduce response time.
    This makes some assumptions about span ordering etc. and also removes any spans that have any overlap with the same span op from consideration.
    """

    __slots__ = ("cumulative_durations", "stored_problems", "spans_involved", "last_span_seen")

    settings_key = DetectorType.SEQUENTIAL_SLOW_SPANS

    def init(self):
        self.cumulative_durations = {}
        self.stored_problems = {}
        self.spans_involved = {}
        self.last_span_seen = {}

    def visit_span(self, span: Span):
        settings_for_span = self.settings_for_span(span)
        if not settings_for_span:
            return
        op, span_id, op_prefix, span_duration, settings = settings_for_span
        duration_threshold = settings.get("cumulative_duration")
        count_threshold = settings.get("count")

        fingerprint = fingerprint_span_op(span)
        if not fingerprint:
            return

        span_end = timedelta(seconds=span.get("timestamp", 0))

        if fingerprint not in self.spans_involved:
            self.spans_involved[fingerprint] = []

        self.spans_involved[fingerprint] += [span_id]

        if fingerprint not in self.last_span_seen:
            self.last_span_seen[fingerprint] = span_end
            self.cumulative_durations[fingerprint] = span_duration
            return

        last_span_end = self.last_span_seen[fingerprint]
        current_span_start = timedelta(seconds=span.get("start_timestamp", 0))

        are_spans_overlapping = current_span_start <= last_span_end
        if are_spans_overlapping:
            del self.last_span_seen[fingerprint]
            self.spans_involved[fingerprint] = []
            self.cumulative_durations[fingerprint] = timedelta(0)
            return

        self.cumulative_durations[fingerprint] += span_duration
        self.last_span_seen[fingerprint] = span_end

        spans_counts = len(self.spans_involved[fingerprint])

        if not self.stored_problems.get(fingerprint, False):
            if spans_counts >= count_threshold and self.cumulative_durations[
                fingerprint
            ] >= timedelta(milliseconds=duration_threshold):
                spans_involved = self.spans_involved[fingerprint]
                self.stored_problems[fingerprint] = PerformanceSpanProblem(
                    span_id, op_prefix, spans_involved
                )


class LongTaskSpanDetector(PerformanceDetector):
    """
    Checks for ui.long-task spans, where the cumulative duration of the spans exceeds our threshold
    """

    __slots__ = ("cumulative_duration", "spans_involved", "stored_problems")

    settings_key = DetectorType.LONG_TASK_SPANS

    def init(self):
        self.cumulative_duration = timedelta(0)
        self.spans_involved = []
        self.stored_problems = {}

    def visit_span(self, span: Span):
        settings_for_span = self.settings_for_span(span)
        if not settings_for_span:
            return
        op, span_id, op_prefix, span_duration, settings = settings_for_span
        duration_threshold = settings.get("cumulative_duration")

        fingerprint = fingerprint_span(span)
        if not fingerprint:
            return

        span_duration = get_span_duration(span)
        self.cumulative_duration += span_duration
        self.spans_involved.append(span_id)

        if self.cumulative_duration >= timedelta(milliseconds=duration_threshold):
            self.stored_problems[fingerprint] = PerformanceSpanProblem(
                span_id, op_prefix, self.spans_involved
            )


class RenderBlockingAssetSpanDetector(PerformanceDetector):
    __slots__ = ("stored_problems", "fcp", "transaction_start")

    settings_key = DetectorType.RENDER_BLOCKING_ASSET_SPAN

    def init(self):
        self.stored_problems = {}
        self.transaction_start = timedelta(seconds=self.event().get("start_timestamp", 0))
        self.fcp = None

        # Only concern ourselves with transactions where the FCP is within the
        # range we care about.
        fcp_hash = self.event().get("measurements", {}).get("fcp", {})
        fcp_value = fcp_hash.get("value")
        if fcp_value and ("unit" not in fcp_hash or fcp_hash["unit"] == "millisecond"):
            fcp = timedelta(milliseconds=fcp_value)
            fcp_minimum_threshold = timedelta(
                milliseconds=self.settings.get("fcp_minimum_threshold")
            )
            fcp_maximum_threshold = timedelta(
                milliseconds=self.settings.get("fcp_maximum_threshold")
            )
            if fcp >= fcp_minimum_threshold and fcp < fcp_maximum_threshold:
                self.fcp = fcp

    def visit_span(self, span: Span):
        if not self.fcp:
            return

        op = span.get("op", None)
        allowed_span_ops = self.settings.get("allowed_span_ops")
        if op not in allowed_span_ops:
            return False

        if self._is_blocking_render(span):
            span_id = span.get("span_id", None)
            fingerprint = fingerprint_span(span)
            if span_id and fingerprint:
                self.stored_problems[fingerprint] = PerformanceSpanProblem(span_id, op, [span_id])

        # If we visit a span that starts after FCP, then we know we've already
        # seen all possible render-blocking resource spans.
        span_start_timestamp = timedelta(seconds=span.get("start_timestamp", 0))
        fcp_timestamp = self.transaction_start + self.fcp
        if span_start_timestamp >= fcp_timestamp:
            # Early return for all future span visits.
            self.fcp = None

    def _is_blocking_render(self, span):
        span_end_timestamp = timedelta(seconds=span.get("timestamp", 0))
        fcp_timestamp = self.transaction_start + self.fcp
        if span_end_timestamp >= fcp_timestamp:
            return False

        span_duration = get_span_duration(span)
        fcp_ratio_threshold = self.settings.get("fcp_ratio_threshold")
        return span_duration / self.fcp > fcp_ratio_threshold


class NPlusOneSpanDetector(PerformanceDetector):
    """
    Checks for multiple concurrent API calls.
    N.B.1. Non-greedy! Returns the first N concurrent spans of a series of
      concurrent spans, rather than all spans in a concurrent series.
    N.B.2. Assumes that spans are passed in ascending order of `start_timestamp`
    N.B.3. Only returns _the first_ set of concurrent calls of all possible.
    """

    __slots__ = ("spans_involved", "stored_problems")

    settings_key = DetectorType.N_PLUS_ONE_SPANS

    def init(self):
        self.spans_involved = {}
        self.most_recent_start_time = {}
        self.most_recent_hash = {}
        self.stored_problems = {}

    def visit_span(self, span: Span):
        settings_for_span = self.settings_for_span(span)
        if not settings_for_span:
            return

        op, span_id, op_prefix, span_duration, settings = settings_for_span

        start_time_threshold = timedelta(milliseconds=settings.get("start_time_threshold", 0))
        count = settings.get("count", 10)

        fingerprint = fingerprint_span_op(span)
        if not fingerprint:
            return

        hash = span.get("hash", None)
        if not hash:
            return

        if fingerprint not in self.spans_involved:
            self.spans_involved[fingerprint] = []
            self.most_recent_start_time[fingerprint] = 0
            self.most_recent_hash[fingerprint] = ""

        delta_to_previous_span_start_time = timedelta(
            seconds=(span["start_timestamp"] - self.most_recent_start_time[fingerprint])
        )

        is_concurrent_with_previous_span = delta_to_previous_span_start_time < start_time_threshold
        has_same_hash_as_previous_span = span["hash"] == self.most_recent_hash[fingerprint]

        self.most_recent_start_time[fingerprint] = span["start_timestamp"]
        self.most_recent_hash[fingerprint] = hash

        if is_concurrent_with_previous_span and has_same_hash_as_previous_span:
            self.spans_involved[fingerprint].append(span)
        else:
            self.spans_involved[fingerprint] = [span_id]
            return

        if not self.stored_problems.get(fingerprint, False):
            if len(self.spans_involved[fingerprint]) >= count:
                self.stored_problems[fingerprint] = PerformanceSpanProblem(
                    span_id, op_prefix, self.spans_involved[fingerprint]
                )


class NPlusOneDBSpanDetector(PerformanceDetector):
    """
    Detector goals:
      - identify a database N+1 query with high accuracy
      - collect enough information to create a good fingerprint (see below)
      - only return issues with good fingerprints

    A good fingerprint is one that gives us confidence that, if two fingerprints
    match, then they correspond to the same issue location in code (and
    therefore, the same fix).

    To do this we look for a specific structure:

      [-------- transaction span -----------]
         [-------- parent span -----------]
            [source query]
                          [n0]
                              [n1]
                                  [n2]
                                      ...

    If we detect two different N+1 problems, and both have matching parents,
    source queries, and repeated (n) queries, then we can be fairly confident
    they are the same issue.
    """

    __slots__ = (
        "stored_problems",
        "potential_parents",
        "source_span",
        "n_hash",
        "n_spans",
    )

    settings_key = DetectorType.N_PLUS_ONE_DB_QUERIES

    def init(self):
        self.stored_problems = {}
        self.potential_parents = {}
        self.n_spans = []
        self.source_span = None

    def visit_span(self, span: Span) -> None:
        span_id = span.get("span_id", None)
        op = span.get("op", None)
        if not span_id or not op:
            return

        if not op.startswith("db"):
            # This breaks up the N+1 we're currently tracking.
            self._maybe_store_problem()
            self._reset_detection()
            # Treat it as a potential parent as long as it isn't the root span.
            if span.get("parent_span_id", None):
                self.potential_parents[span_id] = span
            return

        if not self.source_span:
            # We aren't currently tracking an N+1. Maybe this span triggers one!
            self._maybe_use_as_source(span)
            return

        # If we got this far, we know we're a DB span and we're looking for a
        # sequence of N identical DB spans.
        if self._continues_n_plus_1(span):
            self.n_spans.append(span)
        else:
            self._maybe_store_problem()
            self._reset_detection()
            # Maybe this DB span starts a whole new N+1!
            self._maybe_use_as_source(span)

    def on_complete(self) -> None:
        self._maybe_store_problem()

    def _contains_complete_query(self, span: Span) -> bool:
        # When SDKs truncate span description, they add a "..." suffix (three
        # full stops, not an ellipsis).
        query = span.get("description", None)
        return query and not query.endswith("...")

    def _maybe_use_as_source(self, span: Span):
        if not self._contains_complete_query(span):
            return

        parent_span_id = span.get("parent_span_id", None)
        if not parent_span_id or parent_span_id not in self.potential_parents:
            return

        self.source_span = span

    def _continues_n_plus_1(self, span: Span):
        if not self._contains_complete_query(span):
            return False

        if self._overlaps_last_span(span):
            return False

        expected_parent_id = self.source_span.get("parent_span_id", None)
        parent_id = span.get("parent_span_id", None)
        if not parent_id or parent_id != expected_parent_id:
            return False

        span_hash = span.get("hash", None)
        if not span_hash:
            return False

        if not self.n_hash:
            self.n_hash = span_hash
            return True

        return span_hash == self.n_hash

    def _overlaps_last_span(self, span: Span) -> bool:
        last_span = self.source_span
        if self.n_spans:
            last_span = self.n_spans[-1]

        last_span_ends = timedelta(seconds=last_span.get("timestamp", 0))
        current_span_begins = timedelta(seconds=span.get("start_timestamp", 0))
        return last_span_ends > current_span_begins

    def _maybe_store_problem(self):
        if not self.source_span or not self.n_spans:
            return

        count = self.settings.get("count")
        duration_threshold = timedelta(milliseconds=self.settings.get("duration_threshold"))

        # Do we have enough spans?
        if len(self.n_spans) < count:
            return

        # Do the spans take enough total time?
        total_duration = timedelta()
        for span in self.n_spans:
            total_duration += get_span_duration(span)
        if total_duration < duration_threshold:
            return

        # We require a parent span in order to improve our fingerprint accuracy.
        parent_span_id = self.source_span.get("parent_span_id", None)
        if not parent_span_id:
            return
        parent_span = self.potential_parents[parent_span_id]
        if not parent_span:
            return

        fingerprint = self._fingerprint(
            parent_span.get("op", None),
            parent_span.get("hash", None),
            self.source_span.get("hash", None),
            self.n_spans[0].get("hash", None),
        )
        if fingerprint not in self.stored_problems:
            spans_involved = [self.source_span] + self.n_spans
            span_ids_involved = [span.get("span_id", None) for span in spans_involved]
            self.stored_problems[fingerprint] = PerformanceProblem(
                fingerprint=fingerprint,
                op="db",
                desc=self.source_span.get("description", ""),
                type=GroupType.PERFORMANCE_N_PLUS_ONE_DB_QUERIES,
                spans_involved=span_ids_involved,
            )

    def _reset_detection(self):
        self.source_span = None
        self.n_hash = None
        self.n_spans = []

    def _fingerprint(self, parent_op, parent_hash, source_hash, n_hash) -> str:
        problem_class = GroupType.PERFORMANCE_N_PLUS_ONE_DB_QUERIES
        full_fingerprint = hashlib.sha1(
            (str(parent_op) + str(parent_hash) + str(source_hash) + str(n_hash)).encode("utf8"),
        ).hexdigest()
        return f"1-{problem_class}-{full_fingerprint}"


# Reports metrics and creates spans for detection
def report_metrics_for_detectors(
    event_id: Optional[str], detectors: Dict[str, PerformanceDetector], sdk_span: Any
):
    all_detected_problems = [i for _, d in detectors.items() for i in d.stored_problems]
    has_detected_problems = bool(all_detected_problems)

    if has_detected_problems:
        sdk_span.containing_transaction.set_tag("_pi_all_issue_count", len(all_detected_problems))
        metrics.incr(
            "performance.performance_issue.aggregate",
            len(all_detected_problems),
        )
        if event_id:
            sdk_span.containing_transaction.set_tag("_pi_transaction", event_id)

    detected_tags = {}
    for detector_enum, detector in detectors.items():
        detector_key = detector_enum.value
        detected_problems = detector.stored_problems
        detected_problem_keys = list(detected_problems.keys())
        detected_tags[detector_key] = bool(len(detected_problem_keys))

        if not detected_problem_keys:
            continue

        first_problem = detected_problems[detected_problem_keys[0]]
        if first_problem.fingerprint:
            sdk_span.containing_transaction.set_tag(
                f"_pi_{detector_key}_fp", first_problem.fingerprint
            )

        span_id = (
            first_problem.span_id
            if isinstance(first_problem, PerformanceSpanProblem)
            else first_problem.spans_involved[0]
        )
        sdk_span.containing_transaction.set_tag(f"_pi_{detector_key}", span_id)

        op_tags = {}
        for problem in detected_problems.values():
            op = problem.allowed_op if isinstance(problem, PerformanceSpanProblem) else problem.op
            op_tags[f"op_{op}"] = True
        metrics.incr(
            f"performance.performance_issue.{detector_key}",
            len(detected_problem_keys),
            tags=op_tags,
        )

    metrics.incr(
        "performance.performance_issue.detected",
        instance=str(has_detected_problems),
        tags=detected_tags,
    )
