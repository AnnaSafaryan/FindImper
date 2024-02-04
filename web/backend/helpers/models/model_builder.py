def build_morph(model_name):
    if model_name == 'pym':
        from .pym import Pym
        return Pym
    if model_name == 'mys':
        from .mys import Mys
        return Mys
    if model_name == 'spa':
        from .spa import Spa
        return Spa
    if model_name == 'udp':
        from .udp import Udp
        return Udp
    if model_name == 'sta':
        from .sta import Sta
        return Sta

