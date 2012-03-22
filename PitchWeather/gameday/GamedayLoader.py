import pdb
import sys

class GamedayLoader(object):

    def _xml2obj(attrs, baseballclass):
        """Takes a list of attributes (as returned by BeautifulStoneSoup)
        and a class from baseball.py
        
        Apply those attributes to a new instance of that class."""
        obj = baseballclass()
        for name, val in dict(attrs).iteritems():
            if val == '':
                val = None
            if name in dir(baseballclass):
                try:
                    obj.__setattr__(name, val)
                except TypeError:
                    pdb.set_trace()
                except AttributeError:
                    pdb.set_trace()
                except UnicodeEncodeError:
                    obj.__setattr__(name, None)
        else:
            try:
                print >>sys.stderr, name, val, str(baseballclass)
            except ValueError:
                print >>sys.stderr, name
        return obj

