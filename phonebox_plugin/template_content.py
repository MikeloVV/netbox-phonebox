from netbox.plugins import PluginTemplateExtension


class ContactPhoneNumbers(PluginTemplateExtension):
    """Display phone numbers on contact page"""
    
    model = 'tenancy.contact'
    
    def right_page(self):
        """Add phone numbers panel to contact page"""
        obj = self.context.get('object')
        
        if not obj or not hasattr(obj, 'phone_numbers'):
            return ''
        
        phone_numbers = obj.phone_numbers.all()
        
        if not phone_numbers.exists():
            return ''
        
        return self.render(
            'netbox_phonebox/inc/contact_phone_numbers.html',
            extra_context={
                'phone_numbers': phone_numbers,
                'object_type': 'Contact',
            }
        )


class DevicePhoneNumbers(PluginTemplateExtension):
    """Display phone numbers on device page"""
    
    model = 'dcim.device'
    
    def right_page(self):
        """Add phone numbers panel to device page"""
        obj = self.context.get('object')
        
        if not obj or not hasattr(obj, 'phone_numbers'):
            return ''
        
        phone_numbers = obj.phone_numbers.all()
        
        if not phone_numbers.exists():
            return ''
        
        return self.render(
            'netbox_phonebox/inc/device_phone_numbers.html',
            extra_context={
                'phone_numbers': phone_numbers,
                'object_type': 'Device',
            }
        )


class VirtualMachinePhoneNumbers(PluginTemplateExtension):
    """Display phone numbers on virtual machine page"""
    
    model = 'virtualization.virtualmachine'
    
    def right_page(self):
        """Add phone numbers panel to VM page"""
        obj = self.context.get('object')
        
        if not obj or not hasattr(obj, 'phone_numbers'):
            return ''
        
        phone_numbers = obj.phone_numbers.all()
        
        if not phone_numbers.exists():
            return ''
        
        return self.render(
            'netbox_phonebox/inc/vm_phone_numbers.html',
            extra_context={
                'phone_numbers': phone_numbers,
                'object_type': 'Virtual Machine',
            }
        )


template_extensions = [ContactPhoneNumbers, DevicePhoneNumbers, VirtualMachinePhoneNumbers]