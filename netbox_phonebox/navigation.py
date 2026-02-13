from netbox.plugins import PluginMenuButton, PluginMenuItem, PluginMenu

menu = PluginMenu(
    label='PhoneBox',
    groups=(
        (
            'Phone Numbers',
            (
                PluginMenuItem(
                    link='plugins:netbox_phonebox:phonenumber_list',
                    link_text='Phone Numbers',
                    buttons=(
                        PluginMenuButton(
                            link='plugins:netbox_phonebox:phonenumber_add',
                            title='Add',
                            icon_class='mdi mdi-plus-thick',
                        ),
                    ),
                ),
                PluginMenuItem(
                    link='plugins:netbox_phonebox:telephonyprovider_list',
                    link_text='Providers',
                    buttons=(
                        PluginMenuButton(
                            link='plugins:netbox_phonebox:telephonyprovider_add',
                            title='Add',
                            icon_class='mdi mdi-plus-thick',
                        ),
                    ),
                ),
            ),
        ),
        (
            'PBX',
            (
                PluginMenuItem(
                    link='plugins:netbox_phonebox:pbxserver_list',
                    link_text='PBX Servers',
                    buttons=(
                        PluginMenuButton(
                            link='plugins:netbox_phonebox:pbxserver_add',
                            title='Add',
                            icon_class='mdi mdi-plus-thick',
                        ),
                    ),
                ),
                PluginMenuItem(
                    link='plugins:netbox_phonebox:extension_list',
                    link_text='Extensions',
                    buttons=(
                        PluginMenuButton(
                            link='plugins:netbox_phonebox:extension_add',
                            title='Add',
                            icon_class='mdi mdi-plus-thick',
                        ),
                    ),
                ),
                PluginMenuItem(
                    link='plugins:netbox_phonebox:siptrunk_list',
                    link_text='SIP Trunks',
                    buttons=(
                        PluginMenuButton(
                            link='plugins:netbox_phonebox:siptrunk_add',
                            title='Add',
                            icon_class='mdi mdi-plus-thick',
                        ),
                    ),
                ),
            ),
        ),
        (
            'Call Management',
            (
                PluginMenuItem(
                    link='plugins:netbox_phonebox:calllog_list',
                    link_text='Call Logs',
                ),
                PluginMenuItem(
                    link='plugins:netbox_phonebox:call_statistics',
                    link_text='Call Statistics',
                ),
                PluginMenuItem(
                    link='plugins:netbox_phonebox:make_call',
                    link_text='Make Call',
                    buttons=(
                        PluginMenuButton(
                            link='plugins:netbox_phonebox:make_call',
                            title='Make Call',
                            icon_class='mdi mdi-phone',
                        ),
                    ),
                ),
            ),
        ),
    ),
    icon_class='mdi mdi-phone-classic',
)

# Dashboard link (appears in top menu)
menu_items = (
    PluginMenuItem(
        link='plugins:netbox_phonebox:dashboard',  # ← Исправлено: было phonenumber_dashboard
        link_text='PhoneBox Dashboard',
        permissions=['netbox_phonebox.view_phonenumber'],
    ),
)