from netbox.api.routers import NetBoxRouter

from . import views

router = NetBoxRouter()
router.register("pbx-servers", views.PBXServerViewSet)
router.register("sip-trunks", views.SIPTrunkViewSet)
router.register("phone-numbers", views.PhoneNumberViewSet)

urlpatterns = router.urls