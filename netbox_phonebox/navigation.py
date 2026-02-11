from netbox.plugins import PluginMenuItem, PluginMenuButton

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_phonebox:phonenumber_dashboard',
        link_text='Dashboard',
        permissions=['netbox_phonebox.view_phonenumber'],
        buttons=()
    ),
    PluginMenuItem(
        link='plugins:netbox_phonebox:phonenumber_list',
        link_text='Phone Numbers',
        permissions=['netbox_phonebox.view_phonenumber'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_phonebox:phonenumber_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_phonebox.add_phonenumber']
            ),
            PluginMenuButton(
                link='plugins:netbox_phonebox:phonenumber_import',
                title='Import CSV',
                icon_class='mdi mdi-upload',
                permissions=['netbox_phonebox.add_phonenumber']
            ),
            PluginMenuButton(
                link='plugins:netbox_phonebox:phonenumber_bulk_import',
                title='Bulk Import',
                icon_class='mdi mdi-text-box-multiple',
                permissions=['netbox_phonebox.add_phonenumber']
            ),
            PluginMenuButton(
                link='plugins:netbox_phonebox:phonenumber_export',
                title='Export',
                icon_class='mdi mdi-download',
                permissions=['netbox_phonebox.view_phonenumber']
            ),
        )
    ),
    PluginMenuItem(
        link='plugins:netbox_phonebox:telephonyprovider_list',
        link_text='Providers',
        permissions=['netbox_phonebox.view_telephonyprovider'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_phonebox:telephonyprovider_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_phonebox.add_telephonyprovider']
            ),
        )
    ),
    PluginMenuItem(
        link='plugins:netbox_phonebox:pbxserver_list',
        link_text='PBX Servers',
        permissions=['netbox_phonebox.view_pbxserver'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_phonebox:pbxserver_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_phonebox.add_pbxserver']
            ),
        )
    ),
    PluginMenuItem(
        link='plugins:netbox_phonebox:extension_list',
        link_text='Extensions',
        permissions=['netbox_phonebox.view_extension'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_phonebox:extension_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_phonebox.add_extension']
            ),
            PluginMenuButton(
                link='plugins:netbox_phonebox:make_call',
                title='Make Call',
                icon_class='mdi mdi-phone',
                permissions=['netbox_phonebox.view_extension']
            ),
        )
    ),
    PluginMenuItem(
        link='plugins:netbox_phonebox:siptrunk_list',
        link_text='SIP Trunks',
        permissions=['netbox_phonebox.view_siptrunk'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_phonebox:siptrunk_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_phonebox.add_siptrunk']
            ),
        )
    ),
    PluginMenuItem(
        link='plugins:netbox_phonebox:calllog_list',
        link_text='Call Logs',
        permissions=['netbox_phonebox.view_calllog'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_phonebox:call_statistics',
                title='Statistics',
                icon_class='mdi mdi-chart-bar',
                permissions=['netbox_phonebox.view_calllog']
            ),
        )
    ),
)