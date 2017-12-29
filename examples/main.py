from os import chdir as os_chdir
from pathlib import Path
os_chdir(Path(__file__).resolve().parent)
from sys import path as sys_path
sys_path.append('lib')
import logging
import pyd3ckbase as __


def init(cfg):
    action = cfg.get('action', 'run')
    if action not in ['run']:
        raise __.InitErr('Action "{}" is invalid'.format(action))

    try:
        cfg.update(__.read_file('/tmp/foo.json'))
    except __.Err as e:
        log.debug('Updating cfg failed: %s', e)


try:
    _cfg = __.init(__.get_arg_parser())
    log = logging.getLogger(__name__)
except __.Err as _e:
    __.die(_e)

try:
    log.info('Initializing')
    init(_cfg)
    log.info('Running')
except __.Err as _e:
    __.die(_e)

numStr = __.numrange_to_string([1, 3, 8, 22, 23, 21, 20, 0, 4, 2, 0, 5])
log.info('Numbers as string: %s', numStr)
numList = __.numrange_to_list('0-5,8,20-23')
log.info('Numbers as list: %s', numList)
