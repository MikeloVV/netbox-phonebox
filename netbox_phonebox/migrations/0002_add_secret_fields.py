from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_secrets", "0001_initial"),
        ("netbox_phonebox", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="pbxserver",
            name="secret_login",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="pbxserver_logins",
                to="netbox_secrets.secret",
                verbose_name="Login Secret",
                help_text="Secret containing the login/username.",
            ),
        ),
        migrations.AddField(
            model_name="pbxserver",
            name="secret_password",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="pbxserver_passwords",
                to="netbox_secrets.secret",
                verbose_name="Password Secret",
                help_text="Secret containing the password.",
            ),
        ),
        migrations.AddField(
            model_name="siptrunk",
            name="secret_login",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="siptrunk_logins",
                to="netbox_secrets.secret",
                verbose_name="Login Secret",
                help_text="Secret containing the login/username.",
            ),
        ),
        migrations.AddField(
            model_name="siptrunk",
            name="secret_password",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="siptrunk_passwords",
                to="netbox_secrets.secret",
                verbose_name="Password Secret",
                help_text="Secret containing the password.",
            ),
        ),
    ]