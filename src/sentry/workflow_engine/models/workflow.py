from django.db import models

from sentry.backup.scopes import RelocationScope
from sentry.db.models import DefaultFieldsModel, FlexibleForeignKey, region_silo_model, sane_repr
from sentry.models.owner_base import OwnerModel


@region_silo_model
class Workflow(DefaultFieldsModel, OwnerModel):
    """
    A workflow is a way to execute actions in a specified order.
    Workflows are initiated after detectors have been processed, driven by changes to their state.
    """

    __relocation_scope__ = RelocationScope.Organization
    name = models.CharField(max_length=200)
    organization = FlexibleForeignKey("sentry.Organization")

    # If the workflow is not enabled, it will not be evaluated / invoke actions. This is how we "snooze" a workflow
    enabled = models.BooleanField(default=True)

    # Required as the 'when' condition for the workflow, this evalutes states emitted from the detectors
    when_condition_group = FlexibleForeignKey(
        "workflow_engine.DataConditionGroup", blank=True, null=True
    )

    __repr__ = sane_repr("name", "organization_id")

    class Meta:
        app_label = "workflow_engine"
        db_table = "workflow_engine_workflow"

        constraints = [
            models.UniqueConstraint(
                fields=["name", "organization"], name="unique_workflow_name_per_org"
            )
        ]
