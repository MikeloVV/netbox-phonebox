from netbox.api.routers import NetBoxRouter
from . import views

app_name = 'netbox_phonebox'

router = NetBoxRouter()
router.register('phone-numbers', views.PhoneNumberViewSet)
router.register('telephony-providers', views.TelephonyProviderViewSet)  # Изменено

urlpatterns = router.urls