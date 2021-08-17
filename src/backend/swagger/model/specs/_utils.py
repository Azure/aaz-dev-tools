import os
import logging

logger = logging.getLogger('backend')


def map_path_2_repo(path):
    path = os.path.normpath(path)
    ems = path.split(os.sep)
    idx = ems.index('specification')
    ems = ems[idx:]
    return '/'.join(['https://github.com/Azure/azure-rest-api-specs/tree/master', *ems])

