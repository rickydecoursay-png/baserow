# Generated manually for Organization feature

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import baserow.core.fields
import baserow.core.mixins


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0107_twofactorauthprovidermodel_totpauthprovidermodel_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Organization",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("trashed", models.BooleanField(db_index=True, default=False)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", baserow.core.fields.SyncedDateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=165)),
            ],
            options={
                "abstract": False,
            },
            bases=(
                baserow.core.mixins.HierarchicalModelMixin,
                baserow.core.mixins.TrashableModelMixin,
                baserow.core.mixins.CreatedAndUpdatedOnMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="OrganizationUser",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("trashed", models.BooleanField(db_index=True, default=False)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", baserow.core.fields.SyncedDateTimeField(auto_now=True)),
                (
                    "order",
                    models.PositiveIntegerField(
                        help_text="Unique order that the organization has for the user."
                    ),
                ),
                (
                    "permissions",
                    models.CharField(
                        default="MEMBER",
                        help_text="The permissions that the user has within the organization.",
                        max_length=32,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        help_text="The organization that the user has access to.",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.organization",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="The user that has access to the organization.",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("order",),
                "unique_together": {("user", "organization")},
            },
            bases=(
                baserow.core.mixins.HierarchicalModelMixin,
                baserow.core.mixins.TrashableModelMixin,
                baserow.core.mixins.CreatedAndUpdatedOnMixin,
                baserow.core.mixins.OrderableMixin,
                models.Model,
            ),
        ),
        migrations.AddField(
            model_name="organization",
            name="users",
            field=models.ManyToManyField(
                through="core.OrganizationUser", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
