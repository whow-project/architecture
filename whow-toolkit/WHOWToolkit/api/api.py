from abc import ABC, abstractmethod


class Mapper(ABC):
    
    @abstractmethod
    def map(self):
        pass
    
class TriplestoreManager(ABC):
    
    @abstractmethod
    def load_graphs(self):
        pass
    
    @abstractmethod
    def query(self, querystr: str):
        pass