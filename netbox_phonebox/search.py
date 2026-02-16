from netbox.search import SearchIndex, register_search

from .models import PBXServer, SIPTrunk, PhoneNumber


@register_search
class PBXServerIndex(SearchIndex):
    model = PBXServer
    fields = (
        ("name", 100),
        ("domain", 200),
        ("description", 500),
    )


@register_search
class SIPTrunkIndex(SearchIndex):
    model = SIPTrunk
    fields = (
        ("name", 100),
        ("peer_address", 200),
        ("description", 500),
    )


@register_search
class PhoneNumberIndex(SearchIndex):
    model = PhoneNumber
    fields = (
        ("number", 100),
        ("label", 200),
        ("description", 500),
    )