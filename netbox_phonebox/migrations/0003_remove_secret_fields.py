from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_phonebox", "0002_add_secret_fields"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pbxserver",
            name="secret_login",
        ),
        migrations.RemoveField(
            model_name="pbxserver",
            name="secret_password",
        ),
        migrations.RemoveField(
            model_name="siptrunk",
            name="secret_login",
        ),
        migrations.RemoveField(
            model_name="siptrunk",
            name="secret_password",
        ),
    ]