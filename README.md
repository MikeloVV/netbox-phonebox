# NetBox PhoneBox Plugin

Phone number management plugin for [NetBox](https://github.com/netbox-community/netbox) 4.x.

## Features

- **Phone Numbers** — manage phone numbers with assignment to tenants, sites, devices, VMs, contacts
- **PBX Servers** — track PBX/IP-PBX servers
- **SIP Trunks** — manage SIP trunks linked to PBX servers
- **NetBox Secrets integration** — credentials (login/password) for PBX Servers and SIP Trunks are stored securely via [netbox-secrets](https://github.com/Onemind-Services-LLC/netbox-secrets)
- Full REST API
- Bulk edit / bulk delete / CSV import
- Global search integration
- Tags and custom fields support

## Requirements

| Dependency | Version |
|---|---|
| NetBox | 4.1.0 — 4.4.x |
| netbox-secrets | ≥ 2.0.0 |

## Installation

```bash
pip install netbox-phonebox