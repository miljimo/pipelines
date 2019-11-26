import copy;
from events import Event , BaseObject , EventHandler;
from pipe import Pipe;


PIP_EVENT_INITIAL_STATE    = 0x00;
PIP_EVENT_PROCESSED_STATE  =  0x01;
    
class PipeEvent(Event):
    def __init__(self, pipe, process_data , state  = PIP_EVENT_INITIAL_STATE):
        self.__Pipe  =  pipe;
        self.__ProcessData  =  process_data;
        
    @property
    def Result(self):
        return self.__ProcessData;

    @property
    def Pipe(self):
        return self.__Pipe;
    
class PipeLine(BaseObject):

    def __init__(self, **kwargs):
        self.__ReusePipe = False;
        #inputs
        reuse_pipes = kwargs['keep_pipes'] if('keep_pipes' in kwargs) else False;
        self.Name   = kwargs['name'] if(('name' in kwargs) and (type(kwargs['name']) == str)) else "pipeline";
        
        if(type(reuse_pipes) == bool):
            self.__ReusePipe  =  reuse_pipes;
        self.__Pipes  =  list();
        self.__PipeProcessed  =  EventHandler();
        pass;
    
    @property
    def PipeProcessed(self):
        return self.__PipeProcessed;

    @PipeProcessed.setter
    def PipeProcessed(self, handler):
        if(isinstance(handler, EventHandler)):
               self.__PipeProcessed = handler;
    
    def Pipe(self, pipe):
        if(isinstance(pipe, Pipe)!= True):
            raise TypeError("Expecting a pipe object but {0} given".format(type(pipe)));
        if(self.IsExists(pipe)):
            print("Pipe already exists");
            return ;
        self.Pipes.append(pipe);  
        return self;

    @property
    def Front(self):
        data  =  None;
        if(len(self.Pipes) >0):
            data  = self.Pipes.pop(0);
        return data;

    def IsExists(self, pipe):
        status  =  True;
        
        if(isinstance(pipe, Pipe)):
            status  =  False;
            for tpipe in self.Pipes:
                if(tpipe.Name  == pipe.Name):
                    status  =  True;
                    break;
        return status;

    @property
    def Pipes(self):
        return self.__Pipes;

    def Process(self, data):
        result  =  None;
        if(data != None):
            processing_data  =  copy.deepcopy(data);
            self.__ReuseList =  list();
            
            while(len(self.Pipes) != 0):    
                pipe  =  self.Front;                
                process_result  =  pipe.Process(processing_data);
                if(process_result != None):                    
                    processing_data = process_result;
                if(self.__ReusePipe):
                    self.__ReuseList.append(pipe);
            if(processing_data  != None):
                result = processing_data ;
                self.__Processed(pipe, result);
            self.__Pipes  = self.__ReuseList;
        return result;

    def __Processed(self, pipe,  result):
        if(self.PipeProcessed != None):
            print("Pipe {0} Processing data ={1}".format(pipe.Name, result));
            event  =  PipeEvent(pipe, result, PIP_EVENT_PROCESSED_STATE);
            self.PipeProcessed(event);
           
    
class MulPipe(Pipe):

    def __init__(self, name):
        super().__init__(name);

    def Process(self , data):
        return data * data;


if(__name__ =="__main__"):
    pipeline  =  PipeLine(keep_pipes  = True);
    pipeline.Pipe(Pipe("Placing the order")
                  ).Pipe(Pipe("Validating the order")
                  ).Pipe(Pipe("Processing the order")
                  ).Pipe(MulPipe("Preparing the other re"));
    pipeline.Process(4);
    pipeline.Process(8);
        
        
