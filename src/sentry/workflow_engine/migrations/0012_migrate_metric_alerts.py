# Generated by Django 5.1.1 on 2024-11-08 23:16

from enum import Enum, IntEnum

from django.apps.registry import Apps
from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

from sentry.incidents.grouptype import MetricAlertFire
from sentry.new_migrations.migrations import CheckedMigration
from sentry.utils.query import RangeQuerySetWrapperWithProgressBarApprox


class PriorityLevel(IntEnum):
    LOW = 25
    MEDIUM = 50
    HIGH = 75


class DetectorPriorityLevel(IntEnum):
    OK = 0
    LOW = PriorityLevel.LOW
    MEDIUM = PriorityLevel.MEDIUM
    HIGH = PriorityLevel.HIGH


class IncidentStatus(Enum):
    OPEN = 1
    CLOSED = 2
    WARNING = 10
    CRITICAL = 20


class ActionType(models.TextChoices):
    Notification = "SendNotificationAction"
    TriggerWorkflow = "TriggerWorkflowAction"


class DataSourceType(models.IntegerChoices):
    SNUBA_QUERY_SUBSCRIPTION = 1
    SNUBA_QUERY = 2


class DataConditionGroupType(models.TextChoices):
    ANY = "any"
    ALL = "all"
    NONE = "none"


class AlertRuleStatus(Enum):
    PENDING = 0
    SNAPSHOT = 4
    DISABLED = 5
    NOT_ENOUGH_DATA = 6


def migrate_metric_alerts(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    AlertRule = apps.get_model("sentry", "AlertRule")
    AlertRuleProjects = apps.get_model("sentry", "AlertRuleProjects")
    AlertRuleTrigger = apps.get_model("sentry", "AlertRuleTrigger")
    AlertRuleTriggerAction = apps.get_model("sentry", "AlertRuleTriggerAction")
    # AlertRuleActivity = apps.get_model("sentry", "AlertRuleActivity")
    QuerySubscription = apps.get_model("sentry", "QuerySubscription")
    Incident = apps.get_model("sentry", "Incident")

    DataSource = apps.get_model("sentry", "DataSource")
    DataConditionGroup = apps.get_model("sentry", "DataConditionGroup")
    Workflow = apps.get_model("sentry", "Workflow")
    Detector = apps.get_model("sentry", "Detector")
    DetectorState = apps.get_model("sentry", "DetectorState")
    DataCondition = apps.get_model("sentry", "DataCondition")
    Action = apps.get_model("sentry", "Action")
    DataConditionGroupAction = apps.get_model("sentry", "DataConditionGroupAction")
    DataSourceDetector = apps.get_model("sentry", "DataSourceDetector")
    DetectorWorkflow = apps.get_model("sentry", "DetectorWorkflow")
    WorkflowDataConditionGroup = apps.get_model("sentry", "WorkflowDataConditionGroup")

    for rule in RangeQuerySetWrapperWithProgressBarApprox(AlertRule.objects.all()):
        if rule.status in [AlertRuleStatus.DISABLED, AlertRuleStatus.SNAPSHOT]:
            continue
        # what about the date_added and date_updated fields? can I write to those to preserve history?
        # description column will be added to the Detector model, but at the time of writing it isn't there yet. will need to update this
        # same for threshold_period, will likely be added to the Detector model but isn't there yet
        # AlertRuleActivity creation rows need to be backfilled into the Detector model, needs new created_by and created_at columns

        query_subscription = QuerySubscription.objects.get(snuba_query=rule.snuba_query_id)
        data_source = DataSource.update_or_create(
            organization_id=rule.organization_id,
            query_id=query_subscription.id,
            type=DataSourceType.SNUBA_QUERY_SUBSCRIPTION,
        )
        data_condition_group = DataConditionGroup.update_or_create(
            logic_type=DataConditionGroupType.ANY,
            organization_id=rule.organization_id,
        )
        workflow = Workflow.objects.update_or_create(
            name=rule.name,
            organization_id=rule.organization_id,
            when_condition_group=data_condition_group.id,
        )
        detector = Detector.update_or_create(
            organization_id=rule.organization_id,
            name=rule.name,
            data_sources=data_source,
            workflow_condition_group=data_condition_group.id,
            type=MetricAlertFire.slug,
            owner_user_id=rule.user_id,
            owner_team=rule.team,
        )

        # state is based on incident status
        project = AlertRuleProjects.objects.get(alert_rule_id=rule.id)
        incident = Incident.objects.get_active_incident(
            alert_rule=rule,
            project=project,
            subscription=query_subscription,
        )
        state = DetectorPriorityLevel.OK
        if incident:
            # we have 45 incidents with a status of OPEN
            # but it's all for the same disabled rule, seems like an edge case
            if incident.status == IncidentStatus.CRITICAL.value:
                state = DetectorPriorityLevel.HIGH
            elif incident.status == IncidentStatus.WARNING.value:
                state = DetectorPriorityLevel.MEDIUM

        DetectorState.update_or_create(
            detector=detector.id,
            active=False,  # this column is getting dropped because we can infer whether or not it's active based on the state
            state=state,
        )
        triggers = AlertRuleTrigger.objects.filter(alert_rule_id=rule.id)
        for trigger in triggers:
            condition_result = (
                DetectorPriorityLevel.MEDIUM
                if trigger.label == "warning"
                else DetectorPriorityLevel.HIGH
            )
            DataCondition.update_or_create(
                condition=trigger.threshold_type,
                comparison=trigger.alert_threshold,
                condition_result=condition_result,
                type="metric_alert",  # this will probably change by the time we actually do the migration
            )
            # missing DataConditionDetails because this table doesn't exist yet
        trigger_actions = AlertRuleTriggerAction.objects.filter(
            alert_rule_trigger__in=[trigger.id for trigger in triggers]
        )
        for action in trigger_actions:
            data = {
                "type": action.type,
                "sentry_app_id": action.sentry_app_id,
                "sentry_app_config": action.sentry_app_config,
            }
            action = Action.objects.update_or_create(
                required=False,
                type=ActionType.Notification,  # is this correct?
                data=data,
                integration_id=action.integration_id,
                target_display=action.target_display,
                target_identifier=action.target_identifier,
                target_type=action.target_type,
            )
            DataConditionGroupAction.objects.update_or_create(
                condition_group=data_condition_group.id,
                action=action.id,
            )

        # fill out lookup tables
        DataSourceDetector.objects.update_or_create(
            data_source=data_source.id, detector=detector.id
        )
        DetectorWorkflow.objects.update_or_create(detector=detector.id, workflow=workflow.id)
        WorkflowDataConditionGroup.objects.update_or_create(
            condition_group=data_condition_group.id, workflow=workflow.id
        )
        # AlertRuleTriggerDataCondition doesn't exist yet
        # AlertRuleDetector doesn't exist yet


class Migration(CheckedMigration):
    # This flag is used to mark that a migration shouldn't be automatically run in production.
    # This should only be used for operations where it's safe to run the migration after your
    # code has deployed. So this should not be used for most operations that alter the schema
    # of a table.
    # Here are some things that make sense to mark as post deployment:
    # - Large data migrations. Typically we want these to be run manually so that they can be
    #   monitored and not block the deploy for a long period of time while they run.
    # - Adding indexes to large tables. Since this can take a long time, we'd generally prefer to
    #   run this outside deployments so that we don't block them. Note that while adding an index
    #   is a schema change, it's completely safe to run the operation after the code has deployed.
    # Once deployed, run these manually via: https://develop.sentry.dev/database-migrations/#migration-deployment

    is_post_deployment = True

    dependencies = [
        ("workflow_engine", "0011_action_updates"),
    ]

    operations = [
        migrations.RunPython(
            migrate_metric_alerts,
            migrations.RunPython.noop,
            hints={"tables": ["sentry_alertrule"]},
        ),
    ]
