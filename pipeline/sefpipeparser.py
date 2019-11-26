import os;
from pipe import Pipe;

class SefPipeParser(Pipe):

   def __init__(self):
       super().__init__(".sef file parsing");
       self.__parser = None;
       
   def Process(self, filename):
       status =  False;
       if(os.path.exists(filename) != True):
           raise IOError("file {0} does not exists".format(filename));
       return self.__parser.Parse(filename);
       
