from events  import Event


class IdleEvent(Event):

    def __init__(self, sender):
        super().__init__("idle.event");
        self.__Sender  = sender;

    @property
    def Sender(self):
        return self.__Sender;

class ProcessingEvent(Event):
    
    def __init__(self,sender,  data):
        super().__init__("processing.event");
        self.__Data      = data;
        self.__Sender    = sender;

    @property
    def Data(self):
        return self.__Data;

    @property
    def Sender(self):
        return self.__Sender;
