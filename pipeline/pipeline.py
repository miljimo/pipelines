import copy;
import time;
from events         import Event , BaseObject , EventHandler;
from pipeevent      import PipeEvent;
from pipe           import Pipe;

PIP_EVENT_INITIAL_STATE    = 0x00;
PIP_EVENT_PROCESSED_STATE  =  0x01;
    
class PipeLine(BaseObject):

    def __init__(self, **kwargs):
        self.__ReusePipe     = False;
        self.__IsProcessing =  False;
        #inputs
        reuse_pipes = kwargs['keep_pipes'] if('keep_pipes' in kwargs) else False;
        self.Name   = kwargs['name'] if(('name' in kwargs) and (type(kwargs['name']) == str)) else "pipeline";
        
        if(type(reuse_pipes) == bool):
            self.__ReusePipe  =  reuse_pipes;
        self.__Pipes  =  list();
        self.__PipeProcessed  =  EventHandler();
        pass;

    @property
    def IsProcessing(self):
        return self.__IsProcessing;
    
    @IsProcessing.setter
    def IsProcessing(self, status):
        if(type(status)  == bool):
            self.__IsProcessing = status;
    
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
            IsProcessing     = True;
            
            while((len(self.Pipes) != 0) and (IsProcessing  == True)):    
                pipe  =  self.Front;                
                process_result  =  pipe.Process(processing_data);
                if(process_result == None):
                    break;
                processing_data = process_result;                
                if(self.__ReusePipe):
                    self.__ReuseList.append(pipe);
                self.__Processed(pipe, processing_data);
                
            if(processing_data  != None):
                result      = processing_data ;                
            self.__Pipes    = self.__ReuseList;
            
        return result;

    def __Processed(self, pipe,  result):
        if(self.PipeProcessed != None):           
            event  =  PipeEvent(pipe, result, PIP_EVENT_PROCESSED_STATE);
            self.PipeProcessed(event);


if(__name__ =="__main__"):
    class MulPipe(Pipe):
        def Process(self , data):
            return data * data;
    pipeline  =  PipeLine(keep_pipes  = True);
    pipeline.Pipe(MulPipe("Placing the order")
                  ).Pipe(MulPipe("Validating the order")
                  ).Pipe(Pipe("Processing the order")
                  ).Pipe(MulPipe("Preparing the other re"));
    
    def OnPipeProcessed(event):
         print("Pipe{0} Processing data ={1}".format(event.Pipe.Name, event.Result));
    pipeline.PipeProcessed += OnPipeProcessed;
    start  = 1;
    while(True):
        time.sleep(2);
        start =  pipeline.Process(start);

        
        
