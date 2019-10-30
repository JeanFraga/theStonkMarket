import time


# decorator to tell how long a function runs
def timeit(method):
    def timed(*args, **kw):
        def _pretty(value):
            '''From seconds to Days;Hours:Minutes;Seconds'''

            valueD = (((value/365)/24)/60)
            Days = int(valueD)

            valueH = (valueD-Days)*365
            Hours = int(valueH)

            valueM = (valueH - Hours)*24
            Minutes = int(valueM)

            valueS = (valueM - Minutes)*60
            Seconds = int(valueS)

            return str(Days)+"D:"+str(Hours)+"H:"+str(Minutes)+"M:"+str(Seconds)+"S"

        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print(f'\n{method.__name__} took {_pretty(te-ts)}\n')
        return result
    return timed
