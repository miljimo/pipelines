from events import BaseObject;

class Pipe(BaseObject):

    def __init__(self, pipeName):
        super().__init__();
        self.Name  =  pipeName;
        pass;

    def Process(self, data):
        self.__Data  =  data;
        result  =  None;
        if(self.__Data != None):
            result = data + 1;           
        return result
    
    @property
    def Data(self):
        return self.__Data;



if(__name__ == "__main__"):
    pipe  =  Pipe("Simple");
    result = pipe.Process(5);
    print(result);
