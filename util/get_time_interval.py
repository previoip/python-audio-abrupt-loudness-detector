import time, functools, os

class TimeHandler:
    def __init__(self):
        self.interval = 0

    def __printl(self): print('-'*64)
    def __printnewline(self, n=1): print('\n'*n)

    def begin(self):
        self.__printl()
        print('#'*4,'timer begin','#'*4)
        self.t = time.time()
        self.__printl()
        self.__printnewline()
    
    def get(self):
        self.interval = time.time() - self.t
        return self.interval

    def log(self):
        def secondsToStr(t):
            return "%d:%02d:%02d.%03d" % functools.reduce(lambda ll,b : divmod(ll[0],b) + ll[1:], [(t*1000,),1000,60,60])
        self.__printnewline()
        self.__printl()
        print('runtime: ',secondsToStr(self.interval))
        self.__printl()

    def cls(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
if __name__ == "__main__":
    pass