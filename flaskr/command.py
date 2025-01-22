from flask import Blueprint
from flaskr.user import create_superuser
bp=Blueprint('command',__name__)

@bp.cli.command("create-superuser")
def cli_create_superuser():
    create_superuser()