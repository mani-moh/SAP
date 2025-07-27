args = (3,)
def func(first:int, times:int = 1):
    print(times * first)
f = func
f(1, args)