from events import Event;
from pipe import Pipe;

class PipeEvent(Event):
    def __init__(self, pipe, process_data , state  = 0):
        super().__init__(state);
        if(isinstance(pipe, Pipe) != True):
            raise TypeError("Expecting parameter 2 to be a type of Pipe");
        self.__Pipe  =  pipe;
        self.__ProcessData  =  process_data;
        
    @property
    def Result(self):
        return self.__ProcessData;

    @property
    def Pipe(self):
        return self.__Pipe;
