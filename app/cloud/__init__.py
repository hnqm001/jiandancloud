from flask import Blueprint

cloud = Blueprint('cloud', __name__)

from . import views
from ..models import Permission


@cloud.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
