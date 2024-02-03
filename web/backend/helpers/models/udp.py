import spacy_udpipe
from .spa import Spa
import configparser
from ..config import config

model_name = config.get('Preprocessing parameters', 'udp_name')


class Udp(Spa):
    def __init__(self, negs, stops, needs, filter_dict):
        super().__init__(negs, stops, needs, filter_dict)
        self.analyzer = spacy_udpipe.load(model_name)  # TODO: попробовать другие модели
        self.name = '{}_{}'.format('udp', model_name)
