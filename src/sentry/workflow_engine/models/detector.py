from __future__ import annotations

import builtins
import logging
from typing import TYPE_CHECKING, Any

from django.db import models
from django.db.models import UniqueConstraint

from sentry.backup.scopes import RelocationScope
from sentry.db.models import DefaultFieldsModel, FlexibleForeignKey, region_silo_model
from sentry.issues import grouptype
from sentry.issues.grouptype import GroupType
from sentry.models.owner_base import OwnerModel

if TYPE_CHECKING:
    from sentry.workflow_engine.processors.detector import DetectorHandler

logger = logging.getLogger(__name__)


@region_silo_model
class Detector(DefaultFieldsModel, OwnerModel):
    __relocation_scope__ = RelocationScope.Organization

    organization = FlexibleForeignKey("sentry.Organization", on_delete=models.CASCADE)
    project = FlexibleForeignKey("sentry.Project", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    # The data sources that the detector is watching
    data_sources = models.ManyToManyField(
        "workflow_engine.DataSource", through="workflow_engine.DataSourceDetector"
    )

    # If the detector is not enabled, it will not be evaluated. This is how we "snooze" a detector
    enabled = models.BooleanField(default=True)

    # Optionally set a description of the detector, this will be used in notifications
    description = models.TextField(blank=True, null=True)

    # This represents a time delta, in seconds. If not null, this is used to determine which time
    # window to query to compare the result from the current time_window to.
    comparison_delta = models.IntegerField(null=True)

    # This will emit an event for the workflow to process
    workflow_condition_group = FlexibleForeignKey(
        "workflow_engine.DataConditionGroup",
        blank=True,
        null=True,
        unique=True,
        on_delete=models.SET_NULL,
    )
    type = models.CharField(max_length=200)

    class Meta(OwnerModel.Meta):
        constraints = OwnerModel.Meta.constraints + [
            UniqueConstraint(
                fields=["organization", "name"],
                name="workflow_engine_detector_org_name",
            )
        ]

    @property
    def group_type(self) -> builtins.type[GroupType] | None:
        return grouptype.registry.get_by_slug(self.type)

    @property
    def detector_handler(self) -> DetectorHandler | None:
        group_type = self.group_type
        if not group_type:
            logger.error(
                "No registered grouptype for detector",
                extra={
                    "group_type": str(group_type),
                    "detector_id": self.id,
                    "detector_type": self.type,
                },
            )
            return None

        if not group_type.detector_handler:
            logger.error(
                "Registered grouptype for detector has no detector_handler",
                extra={
                    "group_type": str(group_type),
                    "detector_id": self.id,
                    "detector_type": self.type,
                },
            )
            return None
        return group_type.detector_handler(self)

    def get_audit_log_data(self) -> dict[str, Any]:
        # TODO: Create proper audit log data for the detector, group and conditions
        return {}
