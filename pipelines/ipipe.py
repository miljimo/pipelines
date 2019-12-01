from events import BaseObject;

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
