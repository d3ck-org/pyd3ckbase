def init(cfg):
    data = {'_logLevel': 'WARN', '_moduleLogLevel': 'WARN'}

    if cfg['_stage'] == 'dev':
        data.update({
            '_logLevel': 'DEBUG',
            '_moduleLogLevel': 'WARN',
            '_logFormat': '%(levelname)s: %(message)s'
        })

    return data
