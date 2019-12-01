import queue;
import time;
from events import EventHandler, Event, BaseObject;
from threading import Thread, Lock;
from pipelines.ipipe import IPipe;

THREAD_WAIT_TIME  =  0.01;


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

                

if(__name__ == "__main__"):
    def OnProcessed(event):
        print("Pipe ={0}, Stage 1 ={1}\n".format(event.Sender.Name, event.Data));
    def OnDataRecieved(event):
         print("Pipe ={0}, Stage 2 ={1}\n".format(event.Sender.Name, event.Data));
        
    pipe  =  Pipe(name  =  "Simple", concurrency = False);
    pipe2  =  Pipe(name  =  "Simple2");
    pipe.ProcessedHandler += OnProcessed;
    pipe.LinkedPipe  = pipe2;
    pipe2.ProcessedHandler +=OnDataRecieved;
    pipe.Start();
   
    
    Counter = 0;
    while(pipe.IsProcessing):
        pipe.Jobs.Add(Counter);
        Counter +=1;

    time.sleep(1);
       

