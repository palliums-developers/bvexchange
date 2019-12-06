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
           'level': 'DEBUG',
           'formatter': 'simple',
           'backupCount' : 3,
           'maxBytes' : 1000000 #1M
           },
       # ������ handler
       },
   'loggers':{
       
       'bvelog': {
           # ���� console Handler������ file Handler
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'b2vlog': {
           # ���� console Handler������ file Handler
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'v2blog': {
           # ���� console Handler������ file Handler
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'dbv2blog': {
           # ���� console Handler������ file Handler
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'dbb2vlog': {
           # ���� console Handler������ file Handler
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'blog': {
           # ���� console Handler������ file Handler
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       'vlog': {
           # ���� console Handler������ file Handler
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
        
       # ������ Logger
       }
}

