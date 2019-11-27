
class IQueueReader(object):
    def Read(self):
        raise NotImplementedError("@Read not implemented.");    

class IQueueWriter(object):

    def Write(self, data):
        raise NotImplementedError("@Write not implemented");
