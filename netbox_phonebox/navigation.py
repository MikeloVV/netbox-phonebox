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
        link='plugins:netbox_phonebox:provider_list',
        link_text='Providers',
        permissions=['netbox_phonebox.view_provider'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_phonebox:provider_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_phonebox.add_provider']
            ),
        )
    ),
)