import copy;
from events import Event , BaseObject;


    
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
    


    
class PipeLine(object):

    def __init__(self, **kwargs):
        self.__ReusePipe = False;
        reuse_pipes = kwargs['keep_pipes'] if('keep_pipes' in kwargs) else False;
        if(type(reuse_pipes) == bool):
            self.__ReusePipe  =  reuse_pipes;
        self.__Pipes  =  list();
        pass;
    
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
                    print("Pipe {0} Processing data ={1}".format(pipe.Name, process_result));
                    processing_data = process_result;
                if(self.__ReusePipe):
                    self.__ReuseList.append(pipe);
            if(processing_data  != None):
                result = processing_data ;
            self.__Pipes  = self.__ReuseList;
        return result;


class MulPipe(Pipe):

    def __init__(self, name):
        super().__init__(name);

    def Process(self , data):
        return data * data;


if(__name__ =="__main__"):
    pipeline  =  PipeLine(keep_pipes  = True);
    pipeline.Pipe(Pipe("Start Ording")
                  ).Pipe(Pipe("Checking Order")
                  ).Pipe(Pipe("Retriving Record")
                  ).Pipe(MulPipe("Muli"));
    pipeline.Process(4);
    pipeline.Process(8);
        
        
