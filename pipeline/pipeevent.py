from events import Event;

class PipeEvent(Event):
    def __init__(self, pipe, process_data , state  = 0):
        super().__init__(state);
        self.__Pipe  =  pipe;
        self.__ProcessData  =  process_data;
        
    @property
    def Result(self):
        return self.__ProcessData;

    @property
    def Pipe(self):
        return self.__Pipe;
