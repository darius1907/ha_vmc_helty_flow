from custom_components.vmc_helty_flow.__init__ import VmcHeltyCoordinator
import pytest

class DummyCoordinator:
    def __init__(self, name):
        self.name = name

@pytest.mark.parametrize(
    ("input_name", "expected_slug"),
    [
    ("VMC Helty Living Room", "vmc_helty_living_room"),
        ("Test@Device!#1", "vmc_helty_test_device_1"),
        ("  VMC   ", "vmc_helty_vmc"),
        ("", "vmc_helty_device"),
        ("vmc_helty_custom", "vmc_helty_custom"),
    ("VMC_HELTY_Kitchen", "vmc_helty_kitchen"),
    ],
)
def test_name_slug(input_name, expected_slug):
    class Dummy:
        def __init__(self, name):
            self.name = name
        # Copia la property name_slug dalla classe vera
        name_slug = VmcHeltyCoordinator.name_slug
    dummy = Dummy(input_name)
    assert dummy.name_slug == expected_slug
