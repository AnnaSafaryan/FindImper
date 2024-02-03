from .pym import Pym
from .mys import Mys
from .spa import Spa
from .udp import Udp
from .sta import Sta


def build_morph(model_name):
    name2model = {
        'pym': Pym,
        'mys': Mys,
        'spa': Spa,
        'udp': Udp,
        'sta': Sta,
    }
    return name2model[model_name]


