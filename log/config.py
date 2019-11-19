import logging.config

config = {
   'version': 1,
   'formatters': {
       'simple': {
           'format': '%(asctime)s : %(name)s : %(levelname)s : %(message)s',
           },
       # ������ formatter
       },
   'handlers': {
       'console': {
           'class': 'logging.StreamHandler',
           'level': 'DEBUG',
           'formatter': 'simple'
           },
       'file': {
           'class': 'logging.handlers.RotatingFileHandler',
           'filename': 'bvexchange.log',
           'level': 'ERROR',
           'formatter': 'simple',
           'backupCount' : 3,
           'maxBytes' : 1000000 #1M
           },
       # ������ handler
       },
   'loggers':{
       #'StreamLogger': {
       #    'handlers': ['console'],
       #    'level': 'DEBUG',
       #    },
       'bvelog': {
           # ���� console Handler������ file Handler
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       # ������ Logger
       }
}

