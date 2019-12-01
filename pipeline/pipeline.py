import copy;
import time;
from events         import Event , BaseObject , EventHandler;
from pipeevent      import PipeEvent;
from pipe           import Pipe;

PIP_EVENT_INITIAL_STATE    =  0x00;
PIP_EVENT_PROCESSED_STATE  =  0x01;
PIP_EVENT_COMPLETED        =  0x02;

class PipeLine(Pipe):

    def __init__(self, **kwargs):
        self.__Pipes           =  list();
        super().__init__(**kwargs);
        self.__Completed        =  EventHandler();
        self.__ErrorOccured     =  EventHandler();
       
        
    @property
    def ErrorOccured(self):
        return self.__ErrorOccured;

    @ErrorOccured.setter
    def ErrorOccured(self, handler):
        if(isinstance(handler, EventHandler)):
            self.__ErrorOccured  = handler;
    @property
    def Completed(self):
        return self.__Completed;
    """
        Handle completed events
    """
    @Completed.setter
    def Completed(self, handler):
        if(isinstance(handler, EventHandler)):
            self.__Completed =  handler;
  
    
    def Pipe(self, pipe):
        if(isinstance(pipe, Pipe)!= True):
            raise TypeError("Expecting a pipe object but {0} given".format(type(pipe)));
        if(self.IsExists(pipe)):
            return ;
        if(self.Count ==0):
             self.LinkedPipe = pipe;
        else:
            index = (self.Count  -1);
            temp = self.Pipes[index];
            temp.LinkedPipe  = pipe;
        self.Pipes.append(pipe);  
        return self;

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

    def Start(self):
        # Track the last processing stage
        if(self.Count > 0):
            self.__LastPipe  =  self.Pipes[self.Count -1];
        for pipe in self.Pipes:
            pipe.ProcessedHandler +=self.__DataProcessingInProgress;
        super().Start();

    def Stop(self):
        for pipe in self.Pipes:
            pipe.ProcessedHandler -= self.__DataProcessingInProgress;
            pipe.Stop();
        super().Stop();
        
    @property
    def Count(self):
        return len(self.Pipes);

    def __DataProcessingInProgress(self, event):
        if(event.Sender == self.__LastPipe):            
            if(self.Completed != None):
                self.Completed(event);
        else:
           if(self.ProcessedHandler != None):
               self.ProcessedHandler(event);
       


if(__name__ =="__main__"):
    def OnHandler(event):
        print(event.Sender.Name);
    def OnProcessing(event):
        print(event.Sender.Name);
        
    pipeline  =  PipeLine(concurrency  = True);
    pipeline.Pipe(Pipe(name ="Start Counter"));
    pipeline.Pipe(Pipe(name ="Mulit Counter"));
    pipeline.Pipe(Pipe(name ="Transformer Counter"));
    pipeline.Completed += OnHandler;
    pipeline.ProcessedHandler +=OnProcessing;
    
    pipeline.Start();
    count  = 10;
    try: 
        while(pipeline.IsProcessing):
            pipeline.Jobs.Add(count);
            count +=1;
            
          
            pass;
    except:
        pipeline.Stop();
        print("Completed");

        
        
