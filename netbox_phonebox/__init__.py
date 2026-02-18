from netbox.plugins import PluginConfig


class PhoneBoxConfig(PluginConfig):
    name = "netbox_phonebox"
    verbose_name = "PhoneBox"
    description = "Phone number management plugin for NetBox"
    version = "2.0.1"
    author = "MikeloVV"
    author_email = ""
    base_url = "phonebox"
    min_version = "4.1.0"
    max_version = "4.4.99"
    default_settings = {}


config = PhoneBoxConfig