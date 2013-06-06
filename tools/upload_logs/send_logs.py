#!/usr/bin/env python
'''
Synchronize raw file to dds files
=================================

Algorithm:

    1. Get a list of current objects file
    2. Make a list of missing DDS
    3. Download RAW image
    4. Calculate his MD5
    5. Convert to DDS
    6. Store DDS
    7. Store origial MD5

TODO:

    Check if the dds must be regenerate according to last MD5 pushed

'''

import sys
from os import unlink, listdir
from os.path import dirname, join, exists, basename, realpath
from ConfigParser import ConfigParser
from ftplib import FTP, error_perm
from tempfile import mkstemp
from os import write, close
from functools import partial
from subprocess import Popen, PIPE
from hashlib import md5
from datetime import datetime

import paramiko

def log(text):
    time = datetime.now().isoformat()
    print '#', time, '#', text

# Force mode ?
force = False
if '--force' in sys.argv:
    force = True

# Read configuration
config_keys = ('user', 'password', 'host', 'path')
config_fn = join(dirname(__file__), 'config.ini')
if not exists(config_fn):
    raise Exception('Missing config.ini')

config = ConfigParser()
config.read(join(dirname(__file__), 'config.ini'))
for key in config_keys:
    if not config.get('ftp', key, None):
        raise Exception('Invalid %r in config.ini' % key)

# Connect to ftp
host = config.get('ftp', 'host')
user = config.get('ftp', 'user')
local_path = config.get('ftp', 'local_path')
target_directory = config.get('ftp', 'path')
password = config.get('ftp', 'password')
port = 22
try:
    transport = paramiko.Transport((host, port))

    transport.connect(username = user, password = password)

    sftp = paramiko.SFTPClient.from_transport(transport)
    print 'Connection opened'
    path = target_directory    

    log('=' * 70)
    for filename in listdir(local_path):
        try:
            if sftp.stat(target_directory+filename):
                #file exists we do nothing
                pass
        except:
            #file do not exists, initiate upload
            print 'uploading : ', filename
            sftp.put(local_path+filename, target_directory+filename)


    sftp.close()
    transport.close()
    print 'Connection closed'
except Exception, e:
    print '*** Caught exception: %s: %s' % (e.__class__, e)
    print 'Internet connection probably unavailable'
    try:
        t.close()
    except:
        pass

log('=' * 70)
# ftp = FTP(host, user, password)
# log('Connected to %s' % host)
