def dec(meth):
    def wrapper(*args, **kwargs):
        print "wrapper"
        return meth(*args, **kwargs)
    return wrapper

class FooMeta(type):
    def __new__(cls, name, bases, classdict):
       
        classdict["mymethod"] = dec(classdict["mymethod"])
        return type.__new__(cls, name, bases, classdict)

class Foo(object):
    __metaclass__ = FooMeta
    def mymethod(self):
        print "hey"

    #def __init__(self):
    #    setattr(self, "mymethod", dec(self.mymethod))
    #    import inspect
    #    print inspect.ismethod(self.mymethod)



Foo().mymethod()
#, name))        

#def dec(meth):
#    return meth

#setattr(Foo, "mymethod", dec(Foo.mymethod))

