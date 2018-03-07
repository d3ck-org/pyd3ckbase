class Err(Exception):
    def __init__(self, *args, **kwargs):  #pylint: disable=W0231
        name = self.__class__.__name__
        if len(args) < 1:
            self.code = 0
            self.message = 'Unknown error'
        elif len(args) == 1:
            self.code = 0
            self.message = str(args[0])
        else:
            self.code = int(args[0])
            self.message = str(args[1])
        if len(self.message) > 1000:
            self.message = '{}\n\n        ...[SKIP]...        \n\n{}'.format(
                self.message[:490], self.message[-490:])
        if kwargs:
            for k, v in kwargs.items():
                if k == 'code' or k == 'message' or v is None:
                    continue
                setattr(self, k, v)

    def __str__(self):
        return self.message


class InitErr(Err):
    pass


class DataErr(Err):
    pass


class TimeError(Err):
    pass


class RunErr(Err):
    pass


class SkipErr(Err):
    pass


class IgnoreErr(Err):
    pass


class DiscardErr(Err):
    pass


class UnsupErr(Err):
    pass
