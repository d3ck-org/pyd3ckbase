import sys
from os import environ as os_environ, getpid as os_getpid
#import logging
from pathlib import Path
from uuid import uuid4
from time import clock as time_clock
from argparse import ArgumentParser as ArgParser, Namespace as ArgParserNs
import coloredlogs
from .exception import InitErr


def _get_cfg_fpath(myDpath: str, clargs: ArgParserNs, cfgFpath: str) -> str:
    if 'cfg' in clargs and clargs.cfg:
        return clargs.cfg
    if cfgFpath:
        return cfgFpath
    if os_environ.get('PYD3CK_CFG_FPATH'):
        return os_environ['PYD3CK_CFG_FPATH']
    cfgFpath = Path(myDpath, 'cfg.py')
    if cfgFpath.exists():
        return str(cfgFpath.resolve())
    return str(Path(Path(__file__).parent, 'cfg.py').resolve())


def _get_stage(clargs: ArgParserNs, stage: str) -> str:
    if 'stage' in clargs and clargs.stage:
        return clargs.stage
    if stage:
        return stage
    if os_environ.get('STAGE'):
        return os_environ['STAGE']
    return 'prod'


def get_arg_parser(addBasicFlags: bool=True) -> ArgParserNs:
    p = ArgParser()
    if addBasicFlags:
        p.add_argument(
            '-f',
            '--force',
            action='store_true',
            required=False,
            help='Enable forced mode')
        p.add_argument(
            '-v',
            '--verbose',
            action='store_true',
            required=False,
            help='Enable verbose mode')
        p.add_argument(
            '-Q',
            '--quiet',
            action='store_true',
            required=False,
            help='Enable quiet mode')
        p.add_argument(
            '-C',
            '--cfg',
            action='store',
            required=False,
            help='Path to cfg file')
        p.add_argument(
            '-S', '--stage', action='store', required=False, help='Set stage')
    return p


def init(ap: ArgParserNs=None, **kwargs) -> dict:
    clargs = ap.parse_args() if ap else ArgParserNs()
    myFpath = kwargs.get('_fpath', Path(sys.argv[0]).resolve())
    myDpath = str(myFpath.parent)

    cfg = {
        '_startTime': time_clock(),
        '_fpath': str(myFpath),
        '_dpath': myDpath,
        '_fname': str(myFpath.name),
        '_clargs': clargs,
        '_uuid': str(uuid4()),
        '_pid': os_getpid(),
        '_verbose': False,
        '_quiet': False,
        '_force': False,
        '_logLevel': 'WARN',
        '_moduleLogLevel': 'WARN',
        '_logFormat': '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        '_cfgFpath': _get_cfg_fpath(myDpath, clargs, kwargs.get('cfgFpath')),
        '_stage': _get_stage(clargs, kwargs.get('_stage'))
    }

    if cfg['_cfgFpath']:
        from types import ModuleType
        from importlib.machinery import SourceFileLoader
        try:
            loader = SourceFileLoader('cfg', cfg['_cfgFpath'])
            mod = ModuleType(loader.name)
            loader.exec_module(mod)
            cfg.update(mod.init(cfg))
        except (PermissionError, FileNotFoundError, SystemError, ImportError,
                AttributeError) as e:
            raise InitErr('Loading {} failed: {}'.format(cfg['_cfgFpath'], e))

    for key in ['_cfgFpath', '_stage']:
        if key in kwargs:
            del kwargs[key]
    cfg.update(kwargs)

    if 'force' in clargs and clargs.force:
        cfg['_force'] = True
    if 'verbose' in clargs and clargs.verbose:
        cfg['_verbose'] = True
        cfg['_logLevel'] = 'DEBUG'
        cfg['_moduleLogLevel'] = 'DEBUG'
    if 'quiet' in clargs and clargs.quiet:
        cfg['_quiet'] = True
        cfg['_verbose'] = False
        cfg['_logLevel'] = 'WARN'
        cfg['_moduleLogLevel'] = 'WARN'

    #log = logging.getLogger(__name__)
    # logging.basicConfig(
    #     level=logging.__dict__[cfg['_logLevel']], format=cfg['_logFormat'])
    coloredlogs.install(level=cfg['_logLevel'], fmt=cfg['_logFormat'])
    #log.debug('Bootstrap finished')
    #log.debug('Used cfg file: %s', cfg['_cfgFpath'])

    return cfg
