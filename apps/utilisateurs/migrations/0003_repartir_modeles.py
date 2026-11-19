from django.db import migrations


DESTINATIONS = {
    "accounts": ("loginalert", "loginattempt", "notification"),
    "dashboard": ("activity",),
    "evenements": ("event",),
    "participants": ("participant", "complaint", "document"),
    "prestataires": ("provider", "service", "reservation"),
    "programmes": ("program", "suggestion"),
    "ressources": ("resource", "allocation"),
}


def move_content_types(apps, schema_editor, *, reverse=False):
    # Modifier le libellé en place conserve les clés utilisées par auth_permission
    # et django_admin_log, ainsi que les relations utilisateurs/groupes.
    ContentType = apps.get_model("contenttypes", "ContentType")
    content_types = ContentType.objects.using(schema_editor.connection.alias)
    for target, models in DESTINATIONS.items():
        source, destination = (target, "gestion") if reverse else ("gestion", target)
        for model in models:
            row = content_types.filter(app_label=source, model=model)
            if not row.exists():
                continue
            if content_types.filter(app_label=destination, model=model).exists():
                raise RuntimeError(
                    f"Type de contenu déjà présent pour {destination}.{model}. "
                    "Deux identités existent pour ce modèle. La migration est annulée."
                )
            row.update(app_label=destination)


def forwards(apps, schema_editor):
    move_content_types(apps, schema_editor)


def backwards(apps, schema_editor):
    move_content_types(apps, schema_editor, reverse=True)


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('gestion', '0002_alter_allocation_status_alter_complaint_status_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=[
            migrations.RemoveField(
                model_name='activity',
                name='user',
            ),
            migrations.RemoveField(
                model_name='allocation',
                name='event',
            ),
            migrations.RemoveField(
                model_name='allocation',
                name='resource',
            ),
            migrations.RemoveField(
                model_name='complaint',
                name='participant',
            ),
            migrations.RemoveField(
                model_name='document',
                name='participant',
            ),
            migrations.RemoveField(
                model_name='event',
                name='client',
            ),
            migrations.RemoveField(
                model_name='event',
                name='organizer',
            ),
            migrations.RemoveField(
                model_name='event',
                name='validator',
            ),
            migrations.RemoveField(
                model_name='suggestion',
                name='event',
            ),
            migrations.RemoveField(
                model_name='program',
                name='event',
            ),
            migrations.RemoveField(
                model_name='participant',
                name='event',
            ),
            migrations.RemoveField(
                model_name='reservation',
                name='event',
            ),
            migrations.DeleteModel(
                name='LoginAlert',
            ),
            migrations.DeleteModel(
                name='LoginAttempt',
            ),
            migrations.RemoveField(
                model_name='notification',
                name='user',
            ),
            migrations.RemoveField(
                model_name='participant',
                name='user',
            ),
            migrations.RemoveField(
                model_name='provider',
                name='user',
            ),
            migrations.RemoveField(
                model_name='service',
                name='provider',
            ),
            migrations.RemoveField(
                model_name='reservation',
                name='service',
            ),
            migrations.DeleteModel(
                name='Activity',
            ),
            migrations.DeleteModel(
                name='Allocation',
            ),
            migrations.DeleteModel(
                name='Resource',
            ),
            migrations.DeleteModel(
                name='Complaint',
            ),
            migrations.DeleteModel(
                name='Document',
            ),
            migrations.DeleteModel(
                name='Suggestion',
            ),
            migrations.DeleteModel(
                name='Program',
            ),
            migrations.DeleteModel(
                name='Event',
            ),
            migrations.DeleteModel(
                name='Notification',
            ),
            migrations.DeleteModel(
                name='Participant',
            ),
            migrations.DeleteModel(
                name='Provider',
            ),
            migrations.DeleteModel(
                name='Reservation',
            ),
            migrations.DeleteModel(
                name='Service',
            ),
        ]),
        migrations.RunPython(forwards, backwards),
    ]
