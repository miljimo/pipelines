import copy;
import time;
import queue;
import time;
from events       import EventHandler, Event, BaseObject;
from threading    import Thread, Lock;


THREAD_WAIT_TIME           =  0.01;
PIP_EVENT_INITIAL_STATE    =  0x00;
PIP_EVENT_PROCESSED_STATE  =  0x01;
PIP_EVENT_COMPLETED        =  0x02;

class IdleEvent(Event):

    def __init__(self, sender):
        super().__init__("idle.event");
        self.__Sender  = sender;

    @property
    def Sender(self):
        return self.__Sender;
    
class PipeEvent(Event):
    def __init__(self, pipe, process_data , state  = 0):
        super().__init__(state);
        if(isinstance(pipe, IPipe) != True):
            raise TypeError("Expecting parameter 2 to be a type of Pipe");
        self.__Pipe         =  pipe;
        self.__ProcessData  =  process_data;
        
    @property
    def Result(self):
        return self.__ProcessData;
    
    @property
    def Pipe(self):
        return self.__Pipe;
    
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
    
class IPipe(BaseObject):
    
    def Start(self):
        raise NotImplementedError("@Start : not implemented.");

    def Stop(self):
        raise NotImplementedError("@Stop : not implemented");
    
    @property
    def AllowConcurrency(self):
        raise NotImplementedError("@AllowConcurrency property not implemented");

    @AllowConcurrency.setter
    def AllowConcurrency(self, value):
        raise NotImplementedError("@AllowConcurrency property not implemented");

    @property
    def IsProccessing(self):
        raise NotImplementedError("@IsProccessing property not implemented");

    @IsProccessing.setter
    def IsProccessing(self, value):
        raise NotImplementedError("@IsProccessing property not implemented");


class Pipe(IPipe):

    def __init__(self, *args, **kwargs):
        super().__init__();
        if(len(args)>0):
            if(type(args[0]) == str):
                self.Name = args[0];
        else:
            self.Name             = kwargs['name'] if('name' in kwargs) else '';
        self.__LinkedPipe         = None;        
        self.__AllowConcurrency   = kwargs['concurrency'] if( ('concurrency' in kwargs) and (type(kwargs['concurrency']) == bool)) else False;
        self.__ProcessThread      = None;
        self.__ProcessLockThread  = Lock();
        self.__IsProcessing       = False;
        self.__IdleHandler        = EventHandler();
        self.__ProcessedHandler   = EventHandler();
        self.__Jobs               = Pipe.__JobCollection();
       
    @property
    def AllowConcurrency(self):
        return self.__AllowConcurrency;

    @AllowConcurrency.setter
    def AllowConcurrency(self, status):
        if(type(status) == bool):
            if(self.IsProcessing == True):
                raise ValueError("Unable to set AllowConcurrency when the Pipe is already running");
            self.__AllowConcurrency =  status;

    @property
    def ProcessedHandler(self):
        return self.__ProcessedHandler;

    @ProcessedHandler.setter
    def ProcessedHandler(self, handler):
        if(isinstance(handler , EventHandler) != True):
            raise TypeError("ProcessedHandler : expecting a EventHandler");
        self.__ProcessedHandler  =  handler;
    
    @property
    def Jobs(self):
        return self.__Jobs;

    @property
    def LinkedPipe(self):
        return self.__LinkedPipe;

    @LinkedPipe.setter
    def LinkedPipe(self, pipe):
        if(isinstance(pipe, Pipe)):
            if(self.IsProcessing):
                raise ValueError("Unable to set Linked Pipe when the current pipe is running");
            self.__LinkedPipe = pipe;
    
    @property
    def IdleHandler(self):
        return self.__IdleHandler;

    @IdleHandler.setter
    def IdleHandler(self, handler):
        if(isinstance(handler, EventHandler) != True):
            raise TypeError("@IdleHandler: expecting an eventhandler type");
        self.__IdleHandler = handler;        

    def Start(self):
        self.__ProcessLockThread.acquire();
        if(self.IsProcessing != True):
            self.__ProcessThread  =  Thread(target= self.__ThreadLoop);
            self.__ProcessThread.daemon = True;
            self.__ProcessThread.start();
            
            if(self.LinkedPipe != None):
                self.LinkedPipe.AllowConcurrency  = self.AllowConcurrency;
                if(self.LinkedPipe.IsProcessing != True):
                    self.LinkedPipe.Start();

    def __ThreadLoop(self):
        try:
            self.__IsProcessing  = True;
            self.__ProcessLockThread.release();
            while(self.IsProcessing == True):                
                if(self.Jobs.IsEmpty != True):                
                    data  = self.Jobs.Front;
                    if(data != None):
                        self._OnProcess(data);
                        # If allow concurrency running then terminate the process after once concurrency.
                        if(self.AllowConcurrency != True):
                            self.Stop();
                            break;
                            
                else:                    
                    if(self.IdleHandler != None):
                        self.IdleHandler(IdleEvent(self));
                        time.sleep(THREAD_WAIT_TIME);
                    
        except Exception as err:
            self.Stop();
            raise err;
        finally:
            self.__IsProcessing  = False;
                    
    @property
    def IsProcessing(self):
        return self.__IsProcessing;

    @IsProcessing.setter
    def IsProcessing(self, value):
        if(type(value) == bool):
            if(self.IsProcessing != value):
                if(value == True):
                    self.Start(); # Start the process
                else:
                    self.Stop(); # Stop the process
                
    def Stop(self):
        self.__ProcessLockThread.acquire();
        self.__IsProcessing  = False;
        if(self.__ProcessThread != None):
            self.__ProcessThread.join(THREAD_WAIT_TIME);
            self.__ProcessThread   = None;
            if(self.AllowConcurrency == True):
                if(self.LinkedPipe != None):
                    self.LinkedPipe.Stop();
        self.__ProcessLockThread.release();

    def _OnProcess(self, data):
        if(self.LinkedPipe != None):
            self.LinkedPipe.Jobs.Add(data);
        if(self.ProcessedHandler != None):
            self.ProcessedHandler(ProcessingEvent(self, data));


    class __JobCollection(object):

        def __init__(self):
            self.__JobLocker  = Lock();
            self.__Queue      = queue.Queue()
            self.__JobList    = list();

        def Add(self, data):
            self.__JobLocker.acquire();
            self.__Queue.put(data);       
            self.__JobLocker.release();
        
        @property
        def IsEmpty(self):
            return (self.Count == 0);

        @property
        def Count(self):
            return self.__Queue.qsize();
        
        @property
        def Front(self):
            self.__JobLocker.acquire();
            result  = None;
            if(self.Count > 0):
                result  = self.__Queue.get();
            self.__Queue.task_done();  
            self.__JobLocker.release();
            return result;

"""****************************************************************

****************************************************************"""
class PipeLine(Pipe):

    def __init__(self, **kwargs):
        super().__init__(**kwargs);
        self.__Pipes            =  list();        
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
            pipe.ProcessedHandler += self.__DataProcessingInProgress;
        super().Start();

    def Stop(self):
        super().Stop();
        if(self.AllowConcurrency == True):
            # We must stop all the pipes
            self.__RemoveChildrenHandler();
            for pipe in self.Pipes:
                pipe.Stop();
       

    def __RemoveChildrenHandler(self):
        for pipe in self.Pipes:
            pipe.ProcessedHandler -= self.__DataProcessingInProgress;
            pipe.Stop();
        
    @property
    def Count(self):
        return len(self.Pipes);

    def __DataProcessingInProgress(self, event):
        if(event.Sender == self.__LastPipe):            
            if(self.Completed != None):
                self.Completed(event);
                # Remove all handler when all the task have be done.
                # Remember if the pipes are not running concurrency there it
                # just mean that we dont need handler after the
                # last task is processed.
                if(self.AllowConcurrency != True):
                     self.__RemoveChildrenHandler();
        else:
           if(self.ProcessedHandler != None):
               self.ProcessedHandler(event);

    def Clear(self):
        self.Stop();
        self.Pipes.clear();


if(__name__ =="__main__"):
    def OnHandler(event):
        print(event.Sender.Name);
    def OnProcessing(event):
        print("Pipe ={0}, Stage 1 ={1}\n".format(event.Sender.Name, event.Data));
        
    pipeline  =  PipeLine(name="PipeLine", concurrency  = False);
    pipeline.Pipe(Pipe("Start Counter"));
    pipeline.Pipe(Pipe(name ="Mulit Counter"));
    pipeline.Pipe(Pipe(name ="Transformer Counter"));
    pipeline.Completed += OnHandler;
    pipeline.ProcessedHandler +=OnProcessing;
    
    pipeline.Start();
    count  = 1000;
    try: 
        while(pipeline.IsProcessing):
            pipeline.Jobs.Add(count);
            count +=1;
            pass;
    finally:
        while(pipeline.IsProcessing):
            print("Processing");
            pass; # Block until its finished processing
        pipeline.Stop();
        print("Completed");
    time.sleep(1);

        
        
