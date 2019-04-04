import abc
import collections
import csv
import datetime as dt
import json
import os

import dateutil.parser as dt_parser


class Parser(abc.ABC):
    def __init__(self):
        pass

    @property
    @abc.abstractmethod
    def dict_in(self):
        pass

    def apply_to_nested_dict(self, *keys, fun, raise_error: bool = False, default=None):
        value = self.get(*keys, default=default, raise_error=raise_error)
        return map_to_nested_dict(fun=fun, obj=value, inplace=False) if value is not None else default

    def get(self, *keys, default=None, raise_error=True):
        dict_in = dict(self.dict_in)
        try:
            for k in keys:
                if isinstance(dict_in, collections.abc.Mapping):
                    dict_in = dict_in[k]
                else:
                    raise KeyError
            return dict_in

        except KeyError as err:
            if raise_error:
                raise err
            return default

    @staticmethod
    def mapper(obj, fun):
        if isinstance(obj, collections.abc.Mapping):
            return {k: Parser.mapper(v, fun) for k, v in obj.items()}
        elif isinstance(obj, collections.abc.Iterable) and not isinstance(obj, str):
            return [fun(value) for value in obj]
        else:
            return fun(obj)

    def boolean_string_parser(self, *keys: str, raise_error: bool = True, default: bool = None):
        return self.apply_to_nested_dict(*keys, fun=self.parse_boolean_string, raise_error=raise_error,
                                         default=default)

    def build_full_path(self, *keys, path: str, raise_error: bool = True, default=None):
        return self.apply_to_nested_dict(*keys, fun=lambda x: os.path.join(path, x), raise_error=raise_error,
                                         default=default)

    def date_parser(self, *keys: str, fmt="%d/%m/%Y", raise_error: bool = True, default=None):
        return self.apply_to_nested_dict(*keys, fun=lambda x: dt.datetime.strptime(x, fmt), raise_error=raise_error,
                                         default=default)

    def date_util_parser(self, *keys: str, raise_error: bool = True, default=None, **kwargs):
        dayfirst = kwargs.pop("dayfirst", True)
        yearfirst = kwargs.pop("yearfirst", False)
        return self.apply_to_nested_dict(*keys, fun=lambda x: dt_parser.parse(x, dayfirst=dayfirst, yearfirst=yearfirst,
                                                                              **kwargs), raise_error=raise_error,
                                         default=default)

    def string_parser(self, *keys: str, case: str = None, raise_error: bool = True, default: str = None):
        if case is None:
            funct = str
        elif case.lower().startswith("l"):  # LOWER
            funct = lambda x: str(x).lower()
        elif case.lower().startswith("u"):  # UPPER
            funct = lambda x: str(x).upper()
        else:
            raise ValueError("case must be one of the following: %s" % ({None, "upper", "lower"}))
        return self.apply_to_nested_dict(*keys, fun=funct, raise_error=raise_error, default=default)

    def int_parser(self, *keys: str, raise_error: bool = True, default=None):
        return self.apply_to_nested_dict(*keys, fun=int, raise_error=raise_error, default=default)

    def float_parser(self, *keys: str, raise_error: bool = True, default=None):
        return self.apply_to_nested_dict(*keys, fun=float, raise_error=raise_error, default=default)

    @staticmethod
    def parse_boolean_string(string: str):
        if string.upper() == "FALSE":
            return False
        elif string.upper() == "TRUE":
            return True
        else:
            return KeyError


class CsvFileParser(Parser):
    def __init__(self, file):
        super().__init__()
        with open(file, "r") as handler:
            reader = csv.reader(handler)
            self._dict_in = {row[0]: row[1].strip() for row in reader}

    @property
    def dict_in(self):
        return self._dict_in


class JsonFileParser(Parser):
    def __init__(self, file):
        super().__init__()
        self._dict_in = json_to_dict(file)

    @property
    def dict_in(self):
        return self._dict_in


class DictParser(Parser):
    def __init__(self, dict_: dict):
        super().__init__()
        self._dict_in = dict(dict_)

    @property
    def dict_in(self):
        return self._dict_in


def map_to_nested_dict(fun, obj, inplace=False):
    """
    :return:  dictionary with function applied to nested values
    """
    if inplace:
        def mapper(obj, fun):
            if isinstance(obj, collections.abc.MutableMapping):
                for k, v in obj.items():
                    if isinstance(v, collections.abc.Mapping):
                        mapper(v, fun)
                    else:
                        obj[k] = fun(v)
            else:
                raise TypeError("inplace=True works only on types of collections.abc.MutableMapping")
    else:
        def mapper(obj, fun):
            if isinstance(obj, collections.abc.Mapping):
                return {k: mapper(v, fun) for k, v in obj.items()}
            elif type(obj) == list:
                return [fun(v) for v in obj]
            else:
                return fun(obj)

    return mapper(obj=obj, fun=fun)


def json_to_dict(json_file):
    with open(json_file, 'r') as handle:
        d = json.load(handle)
    return d
