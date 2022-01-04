import os

SWAGGER_PATH = os.environ.get("AAZ_SWAGGER_PATH", None)

# Flask configurations
STATIC_FOLDER = '../../web/build'
STATIC_URL_PATH = '/'
