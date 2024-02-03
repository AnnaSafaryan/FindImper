import spacy_stanza
from .spa import Spa
from ..config import config
model_name = config.get('Preprocessing parameters', 'sta_name')


class Sta(Spa):
    def __init__(self, negs, stops, needs, filter_dict):
        super().__init__(negs, stops, needs, filter_dict)
        self.analyzer = spacy_stanza.load_pipeline(model_name)
        self.name = '{}_{}'.format('sta', model_name)
