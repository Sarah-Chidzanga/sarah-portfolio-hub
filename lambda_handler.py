from apig_wsgi import make_lambda_handler
from app import create_app

_app = create_app()
handler = make_lambda_handler(_app)
