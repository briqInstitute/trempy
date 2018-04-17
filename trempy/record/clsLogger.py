"""This module contains ensures that all events are logged properly."""
from trempy.shared.clsBase import BaseCls


class LoggerCls(BaseCls):
    """This class manages the record of events."""
    def __init__(self):
        self.attr = dict()
        self.attr['errors'] = []

    def record_event(self, error_code):
        """This method records the error codes of events."""
        self.attr['errors'].append(error_code)

    def flush(self, outfile):
        """This method records all things related to an evaluation"""
        for error_code in set(self.attr['errors']):
            msg = '\n Warning: '

            if error_code == 0:
                msg += 'small adjustment to bounds in to_real()'
            elif error_code == 1:
                msg += 'Overflow, FloatingPoint errors in _to_interval()'
            elif error_code == 2:
                msg += 'ValueError: f(a) and f(b) must have different signs for brenth()'
            elif error_code == 3:
                msg += 'FloatingPointError: invalid value encountered in double_scalars in utility'
            else:
                raise NotImplementedError

            outfile.write(msg + '\n')

        # Reset the container for the error cases.
        self.attr['errors'] = []


logger_obj = LoggerCls()