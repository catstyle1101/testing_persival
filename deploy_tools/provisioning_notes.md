Обеспечение работы нового сайта 
================================ 
## Необходимые пакеты:
* nginx
* Python 3.6
* virtualenv + pip * Git

например, в Ubuntu:
- sudo add-apt-repository ppa:fkrull/deadsnakes

## Конфигурация виртуального узла Nginx

/etc/nginx/sites-available/SITENAME.conf

* см. nginx.template.conf
* заменить SITENAME, например, на staging.my-domain.com
* изменить в /etc/nginx/mime.types строку из файла mime.types


## Служба Systemd
/etc/systemd/system/SITENAME.service
* см. gunicorn-systemd.template.service
* заменить SITENAME, например, на staging.my-domain.com

## Структура папок:
Если допустить, что есть учетная запись пользователя в /home/username

```text
/home/username 
└── sites
    └── SITENAME 
        ├── database
        ├── source 
        ├── static 
        └── virtualenv```
