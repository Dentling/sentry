# Generated by Django 5.0.3 on 2024-04-24 18:31

import django.db.models.deletion
from django.db import migrations

import sentry.db.models.fields.foreignkey
import sentry.db.models.fields.hybrid_cloud_foreign_key
from sentry.new_migrations.migrations import CheckedMigration


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

    is_post_deployment = False

    dependencies = [
        ("sentry", "0704_backfill_rule_user_team"),
    ]

    operations = [
        migrations.AddField(
            model_name="grouphistory",
            name="team",
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to="sentry.team"
            ),
        ),
        migrations.AddField(
            model_name="grouphistory",
            name="user_id",
            field=sentry.db.models.fields.hybrid_cloud_foreign_key.HybridCloudForeignKey(
                "sentry.User", db_index=True, null=True, on_delete="SET_NULL"
            ),
        ),
    ]
