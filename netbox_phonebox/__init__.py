from netbox.plugins import PluginConfig

class PhoneBoxConfig(PluginConfig):
    name = 'netbox_phonebox'
    verbose_name = 'PhoneBox'
    description = 'Phone number and PBX management for NetBox'
    version = '1.2.1'
    author = 'Mikhail Voronov'
    author_email = 'mikhail.voronov@gmail.com'
    base_url = 'phonebox'
    min_version = '4.0.0'
    max_version = '4.9.99'
    required_settings = []
    default_settings = {
        'default_country_code': '+7',
        'enable_qr_codes': True,
    }

config = PhoneBoxConfig
