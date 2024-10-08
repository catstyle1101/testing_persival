import string

from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
import random

REPO_URL = "https://github.com/catstyle1101/testing_persival"


def deploy():
    """Deploy a fabric package."""
    site_folder = f"/home/www/sites/{env.host}"
    source_folder = site_folder + "/source"
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)


def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ["database", "static", "virtualenv", "source"]:
        run(f"mkdir -p {site_folder}/{subfolder}")


def _get_latest_source(source_folder):
    if exists(f"{source_folder}" + "/.git"):
        run(f"cd {source_folder} && git fetch")
    else:
        run(f"git clone {REPO_URL} {source_folder}")
    current_commit = str(local("git log -n 1 --format=%H", capture=True)).strip("'")
    run(f"cd {source_folder} && git reset --hard {current_commit}")


def _update_settings(source_folder, site_name):
    settings_path = f"{source_folder}/superlists/settings.py"
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(
        settings_path,
        r"ALLOWED_HOSTS = \[\]",
        rf"ALLOWED_HOSTS = \[\"{site_name}\"\]",
    )
    secret_key_file = source_folder + "/superlists/secret_key.py"
    if not exists(secret_key_file):
        chars = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
        key = "".join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, f"SECRET_KEY = '{key}'")
    append(settings_path, "\nfrom .secret_key import SECRET_KEY\n")


def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder.removesuffix("source/") + "/virtualenv"
    if not exists(virtualenv_folder):
        run(f"python3.11 -m venv {virtualenv_folder}")
    run(f"{virtualenv_folder}/bin/pip install -r {source_folder}/requirements.txt")


def _update_static_files(source_folder):

    run(
        f"cd {source_folder} &&"
        f"{source_folder.removesuffix('source/')}/virtualenv/bin/python manage.py collectstatic --noinput"
    )


def _update_database(source_folder):
    run(
        f"cd {source_folder} &&"
        f"{source_folder.removesuffix('source/')}/virtualenv/bin/python "
        f"manage.py migrate --noinput"
    )
