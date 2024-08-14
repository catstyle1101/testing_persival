from fabric.context_managers import settings
from fabric.operations import run


def _get_manage_dot_py(host):
    return f"~/sites/{host}/virtualenv/bin/python ~/sites/{host}/source/manage.py"


def reset_database(host):
    manage_dot_py = _get_manage_dot_py(host)
    with settings(host_string=f"www@{host}"):
        run(f"{manage_dot_py} flush --noinput")


def create_session_on_server(host, email):
    manage_dot_py = _get_manage_dot_py(host)
    with settings(host_string=f"www@{host}"):
        session_key = run(f"{manage_dot_py} create session {email}")
        return session_key.strip()
