from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem


phone_numbers_buttons = [
    PluginMenuButton(
        link="plugins:netbox_phonebox:phonenumber_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    ),
    PluginMenuButton(
        link="plugins:netbox_phonebox:phonenumber_import",
        title="Import",
        icon_class="mdi mdi-upload",
    ),
]

pbx_server_buttons = [
    PluginMenuButton(
        link="plugins:netbox_phonebox:pbxserver_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    ),
    PluginMenuButton(
        link="plugins:netbox_phonebox:pbxserver_import",
        title="Import",
        icon_class="mdi mdi-upload",
    ),
]

sip_trunk_buttons = [
    PluginMenuButton(
        link="plugins:netbox_phonebox:siptrunk_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    ),
    PluginMenuButton(
        link="plugins:netbox_phonebox:siptrunk_import",
        title="Import",
        icon_class="mdi mdi-upload",
    ),
]

menu = PluginMenu(
    label="PhoneBox",
    groups=(
        (
            "Phone Numbers",
            (
                PluginMenuItem(
                    link="plugins:netbox_phonebox:phonenumber_list",
                    link_text="Phone Numbers",
                    buttons=phone_numbers_buttons,
                ),
            ),
        ),
        (
            "PBX",
            (
                PluginMenuItem(
                    link="plugins:netbox_phonebox:pbxserver_list",
                    link_text="PBX Servers",
                    buttons=pbx_server_buttons,
                ),
                PluginMenuItem(
                    link="plugins:netbox_phonebox:siptrunk_list",
                    link_text="SIP Trunks",
                    buttons=sip_trunk_buttons,
                ),
            ),
        ),
    ),
    icon_class="mdi mdi-phone",
)