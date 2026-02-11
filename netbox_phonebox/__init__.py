from netbox.plugins import PluginConfig

class PhoneBoxConfig(PluginConfig):
    name = 'netbox_phonebox'
    verbose_name = 'PhoneBox'
    description = 'Phone number management for NetBox with validation and normalization'
    version = '1.1.2'
    author = 'Mikhail Voronov'
    author_email = 'mikhail.voronov@gmail.com'
    base_url = 'phonebox'
    min_version = '4.0.0'
    max_version = '4.9.99'
    required_settings = []
    default_settings = {
        'default_country_code': 'RU',
        'enable_qr_codes': True,
    }

config = PhoneBoxConfig
