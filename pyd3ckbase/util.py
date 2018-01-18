import logging
from sys import stderr as sys_stderr, exit as sys_exit
from typing import Union, Any, List
from pathlib import Path
from itertools import chain
from re import sub as re_sub, match as re_match
from uuid import UUID, uuid4
from math import floor as math_floor, log10 as math_log10
from pickle import PickleError, load as pickle_load, dump as pickle_dump
from json import load as json_load, dump as json_dump, dumps as json_dumps
from configparser import ConfigParser, Error as configparserError
from mimetypes import guess_type as guess_mime_type
from pendulum import now as pndlm_now
from .exception import DataErr

log = logging.getLogger(__name__)


def stderr(msg: str):
    print(msg, file=sys_stderr)


def stdout(msg: str):
    print(msg)


def stdout_json(data: Any):
    stdout(to_json(data))


def die(msg: str='Unknown', exitCode: int=1):
    stderr('ERROR: {}'.format(msg))
    sys_exit(exitCode)


def cap(v: str) -> str:
    return re_sub('([a-zA-Z])', lambda x: x.groups()[0].upper(), v, 1)


def now(tz='UTC') -> str:
    return pndlm_now(tz).to_iso8601_string()


def to_json(data: Any) -> str:
    try:
        return json_dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
    except (ValueError, KeyError, TypeError) as e:
        raise DataErr('Converting to JSON failed: {}'.format(e))


def to_uuid(uid: str) -> UUID:
    return UUID(str(uid))


def get_uuid(ilk: str='bin') -> Union[UUID, str]:
    return get_uuids(1, ilk)[0]


def get_uuids(cnt: int, ilk: str='bin') -> List[Union[UUID, str]]:
    return [str(uuid4()) for i in range(0, cnt)
            ] if ilk == 'str' else [uuid4() for i in range(0, cnt)]


def is_uuid(uid: Union[str, UUID]) -> bool:
    if isinstance(uid, UUID):
        return True
    try:
        UUID(uid)
    except (ValueError, TypeError, AttributeError):
        return False
    return True


def mkdir(dpath: Union[str, Path], **kwargs):
    # https://docs.python.org/3/library/pathlib.html#pathlib.Path.mkdir
    #   mode=0o777
    #   parents=False
    #   exist_ok=False
    kwargs['parents'] = True if 'parents' not in kwargs else kwargs['parents']
    kwargs['exist_ok'] = True if 'exist_ok' not in kwargs else kwargs[
        'exist_ok']
    dpath = dpath if isinstance(dpath, Path) else Path(dpath)
    log.debug('Creating %s/', dpath)
    try:
        dpath.mkdir(**kwargs)
    except (OSError, IOError, PermissionError, FileNotFoundError,
            FileExistsError) as e:
        raise DataErr('Creating {}/ failed: {}'.format(dpath, e))


def read_file(fpath: Union[str, Path], **kwargs) -> Any:
    enc = kwargs.get('enc', 'utf-8')
    fpath = fpath if isinstance(fpath, Path) else Path(fpath)
    fsfx = ('.' + kwargs['type']) if 'type' in kwargs else fpath.suffix
    data = None
    log.debug('Reading %s', fpath)

    def get_type():
        if fsfx == '.json':
            return 'json'
        if fsfx == '.ini':
            return 'ini'
        if fsfx == '.pickle':
            return 'pickle'
        if fsfx in ['.txt', '.xml', '.csv', '.html', '.css']:
            return 'txt'
        if (guess_mime_type(str(fpath))[0] or 'none').split('/')[0] == 'text':
            return 'txt'
        return 'bin'

    try:
        if get_type() == 'json':
            with open(fpath, 'rt', encoding=enc) as f:
                data = json_load(f)
        elif get_type() == 'ini':
            prsr = ConfigParser()
            # support only simple ini- (properties-) file:
            #   fake section needed by ConfigParser:
            #     https://stackoverflow.com/a/26859985
            with open(fpath, 'rt', encoding='utf-8') as lines:
                lines = chain(('[default]', ), lines)
                prsr.read_file(lines)
            data = dict(prsr['default'])
        elif get_type() == 'pickle':
            with open(fpath, 'rb') as f:
                data = pickle_load(f)
        elif get_type() == 'txt':
            with open(fpath, 'rt', encoding=enc) as f:
                #data = f.read().encode('ascii', 'ignore')
                #data = data.decode('utf-8')
                data = f.read()
        else:  # bin
            with open(fpath, 'rb') as f:
                data = f.read()
    except (OSError, IOError, PermissionError, FileNotFoundError, ValueError,
            PickleError, TypeError, configparserError) as e:
        raise DataErr('Reading file {} failed: {}'.format(fpath, e))
    return data


def write_file(fpath: Union[str, Path], data: Any, **kwargs):
    append = kwargs.get('append', kwargs.get('a', False))
    enc = kwargs.get('enc', 'utf-8')
    fpath = fpath if isinstance(fpath, Path) else Path(fpath)
    fsfx = ('.' + kwargs['type']) if 'type' in kwargs else fpath.suffix
    log.debug('Writing %s', fpath)

    def get_type():
        if fsfx == '.json':
            return 'json'
        if fsfx == '.pickle':
            return 'pickle'
        if isinstance(data, str):
            return 'txt'
        return 'bin'

    try:
        if get_type() == 'json':
            with open(fpath, ('a' if append else 'wt'), encoding=enc) as f:
                json_dump(
                    data, f, ensure_ascii=False, indent=2, sort_keys=True)
        elif get_type() == 'txt':
            with open(fpath, ('a' if append else 'wt'), encoding=enc) as f:
                f.write(data)
        elif get_type() == 'pickle':
            with open(fpath, 'wb') as f:
                pickle_dump(data, f)
        else:  # bin
            with open(fpath, 'wb') as f:
                f.write(data)
    except (OSError, IOError, PermissionError, FileNotFoundError, ValueError,
            TypeError) as e:
        raise DataErr('Writing file {} failed: {}'.format(fpath, e))


def san(d: Any, **kwargs) -> str:
    # w: remove all tabs, newlines and multiple whitespaces
    # nw (no whitespaces): remove all tabs, newlines and whitespaces
    # up: convert to upper case
    # lo: convert to lower case
    # cap: capitalize
    d = str(d)
    if kwargs.get('nw', False):
        # remove all tabs, newlines, spaces
        d = ''.join(d.split()).strip()
    else:
        if kwargs.get('w', True):
            # remove tabs, newlines, multiple spaces
            d = ' '.join(d.split()).strip()
            d.lstrip()
            d.rstrip()
    if kwargs.get('up', False):
        d = d.upper()
    if kwargs.get('lo', False):
        d = d.lower()
    if kwargs.get('cap', False):
        d = cap(d)
    return d


def pp_num(num: int) -> str:
    num = int(num)
    if num == 0:
        return '0'
    names = ['', 'K', 'M', 'B', 'T']
    num2 = float(num)
    m = max(0, min(len(names) - 1, int(math_floor(math_log10(abs(num2)) / 3))))
    num2 = math_floor(num2 / 10**(3 * m) * 10) / 10
    if (int(num2) == num2) or (num2 >= 100):
        num3 = '{}{}'.format(int(num2), names[m])
    else:
        num3 = '{:.1f}{}'.format(num2, names[m])
    return str(num3)


def numrange_to_string(numRng: list, sep: str=',') -> str:
    if not numRng:
        return ''
    try:
        numRng = [int(num) for num in set(numRng)]
    except ValueError:
        raise DataErr('Invalid number range')
    rngs = []
    rng = []
    last = None
    for num in sorted(numRng):
        if last is None or last + 1 == num:
            rng.append(str(num))
        else:
            rngs.append(rng[:])
            rng = [str(num)]
        last = num
    if rng:
        rngs.append(rng)
    pp_rngs = []
    for rng in rngs:
        if len(rng) > 1:
            pp_rngs.append('{}-{}'.format(rng[0], rng[-1]))
        else:
            pp_rngs.append(rng[0])
    return sep.join(pp_rngs)


def numrange_to_list(nums: str) -> list:
    rng = []
    for it in san(nums, nw=True).split(','):
        if it is None or it == '':
            continue
        if it.isdigit():
            rng.append(it)
        elif re_match(r'^\d+\-\d+$', it):
            parts = it.split('-')
            first = int(parts[0])
            last = int(parts[1])
            if first > last:
                raise DataErr('Invalid number range')
            rng += [str(num) for num in range(first, last + 1)]
        else:
            raise DataErr('Invalid number range')
    return [int(num) for num in rng]


def dump(data: Any):
    import pprint
    stdout('===================================')
    pprint.pprint(data)
    stdout('===================================')
