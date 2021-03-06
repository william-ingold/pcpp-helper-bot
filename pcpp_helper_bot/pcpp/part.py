from dataclasses import dataclass


@dataclass(frozen=True)
class Part:
    """Simple immutable dataclass to hold PC part data."""

    __slots__ = ['component', 'name', 'url', 'price', 'vendor', 'vendor_aff_url', 'vendor_url']
    component: str
    name: str
    url: str
    price: str
    vendor: str
    vendor_aff_url: str
    vendor_url: str
