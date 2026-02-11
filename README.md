# NetBox PhoneBox

Advanced phone number and PBX management plugin for NetBox with E.164 validation, Asterisk/FreePBX integration, and call logging.

## Features

### Phase 1 ✅ (Completed)
- **Phone Number Validation** - Automatic validation using `phonenumbers` library
- **E.164 Normalization** - All numbers stored in standardized E.164 format
- **Country Detection** - Automatic country code detection
- **Dashboard** - Statistics, charts, and overview
- **Template Extensions** - Phone numbers displayed on Contact/Device/VM pages
- **Import/Export** - CSV import/export with bulk operations
- **Multiple Formats** - Display in International, National, E.164, RFC3966 formats
- **Click-to-Call** - Direct calling links (tel: URI)
- **QR Codes** - Generate QR codes for easy contact sharing
- **Carrier Detection** - Automatic carrier name detection
- **Geolocation** - Geographic location information
- **Timezone** - Timezone information for numbers

### Phase 2 ✅ (Completed)
- **PBX Integration** - Asterisk/FreePBX support via AMI (Asterisk Manager Interface)
- **Extensions Management** - SIP/PJSIP/IAX2 extension configuration
- **SIP Trunks** - SIP trunk configuration and management
- **Call Logging** - Automatic call history logging
- **Click-to-Call via PBX** - Initiate calls through PBX
- **Call Statistics** - Detailed call analytics and reporting
- **Real-time Status** - PBX server status monitoring
- **Call Recordings** - Link to call recordings

## Installation

### Requirements
- NetBox 4.0.0 or later
- Python 3.10 or later
- Asterisk/FreePBX (optional, for PBX features)

### Install from GitHub

```bash
pip install git+https://github.com/MikeloVV/netbox-phonebox.git