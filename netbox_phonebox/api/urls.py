from netbox.api.routers import NetBoxRouter
from . import views

app_name = 'netbox_phonebox'

router = NetBoxRouter()
router.register('phone-numbers', views.PhoneNumberViewSet)
router.register('telephony-providers', views.TelephonyProviderViewSet)
router.register('pbx-servers', views.PBXServerViewSet)
router.register('sip-trunks', views.SIPTrunkViewSet)
router.register('extensions', views.ExtensionViewSet)
router.register('call-logs', views.CallLogViewSet)

urlpatterns = router.urls