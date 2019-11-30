from events import EventHandler, Event, BaseObject;
from threading import Thread, Lock;
import queue;

THREAD_WAIT_TIME  =  100/1000;

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



class Pipe(BaseObject):

    def __init__(self, **kwargs):
        super().__init__();
        self.__LinkedPipe = None;
        name  = kwargs['name'] if('name' in kwargs) else '';
        link  = kwargs['link'] if('link' in kwargs) else None;
        if(isinstance(link, Pipe)):
           self.__LinkedPipe  = link;
           
        self.Name                 = name;
        self.__ProcessThread      = None;
        self.__ProcessLockThread  =  Lock();
        self.__IsProcessing       = False;
        self.__IdleHandler        = EventHandler();
        self.__ProcessedHandler   = EventHandler();
        self.__Jobs               = Pipe.__JobCollection();

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
            

    def __ThreadLoop(self):
        self.__IsProcessing  = True;
        self.__ProcessLockThread.release();
        while(self.IsProcessing):
            #Process job queue
            if(self.Jobs.IsEmpty != True):                
                data  = self.Jobs.Front;
                if(data != None):
                    self._OnProcess(data);
            else:
                # Idle stage for the pipe
                if(self.IdleHandler != None):
                    self.IdleHandler(IdleEvent(self));
                    
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
        print("Stage 1 ={0}\n".format(event.Data));
    def OnDataRecieved(e):
        print("Stage 2 ={0}\n".format(e.Data));
        
    pipe  =  Pipe(name  =  "Simple");
    pipe2  =  Pipe(name  =  "Simple2");
    pipe.ProcessedHandler += OnProcessed;
    pipe.LinkedPipe  = pipe2;
    pipe2.ProcessedHandler +=OnDataRecieved;
    pipe.Start();
    pipe2.Start();
    Counter = 0;
    while(pipe.IsProcessing):
        pipe.Jobs.Add(Counter);
        Counter +=1;
       
        if(Counter == 20):
            print("\nDone\n");
            pipe.Stop();
            pipe2.Stop();
        

