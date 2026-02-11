from netbox.api.routers import NetBoxRouter
from . import views

app_name = 'netbox_phonebox'

router = NetBoxRouter()
router.register('phone-numbers', views.PhoneNumberViewSet)
router.register('providers', views.ProviderViewSet)

urlpatterns = router.urls