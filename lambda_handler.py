from mangum import Mangum
from app import create_app

_app = create_app()
handler = Mangum(_app, lifespan='off')
