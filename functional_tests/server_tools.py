from fabric.api import run
from fabric.context_managers import settings

# пользователь с правами root на сервере
USER = 'klim'

def _get_manage_dot_py(host):
    '''получить manage.py'''
    return f'~/sites/{host}/virtualenv/bin/python ~/sites/{host}/source/manage.py'

def reset_database(host):
    '''обнулить базу данных'''
    manage_dot_py = _get_manage_dot_py(host)
    with settings(host_string=f'{USER}@{host}'):
        run(f'{manage_dot_py} flush --noinput')

def create_session_on_server(host, email):
    '''создать сеанс на сервере'''
    manage_dot_py = _get_manage_dot_py(host)
    with settings(host_string=f'{USER}@{host}'):
        session_key = run(f'{manage_dot_py} create_session {email}')
        return session_key.strip()