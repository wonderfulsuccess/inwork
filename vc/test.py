def logger(func):
    def wrapper(*args, **kwargs):
        # args是一个数组，kwargs一个字典
        print(args[0].name)
        return func(*args, **kwargs)
    return wrapper

class Test():
    def __init__(self, name):
        self.name = name

    @logger
    def add(self,x,y):
        print(x+y)

if __name__ == '__main__':
    print('asdfasdfas')
    t = Test('Frank')
    t.add(1,2)
