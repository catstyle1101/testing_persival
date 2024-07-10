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
        └── virtualenv
```

## Fabric3 deploy


On computer
```
pip install fabric3
fab deploy --host=mysite.name
```

On server
```
export SITE_URL=mysite.name

sed "s/SITENAME/$SITE_URL/g" source/deploy_tools/nginx.template.conf | sudo tee /etc/nginx/sites-available/$SITE_URL

sudo ln -s ../sites-available/$SITE_URL /etc/nginx/sites-enabled/$SITE_URL

sed "s/SITENAME/$SITE_URL/g" source/deploy_tools/gunicorn-systemd.template.service | sudo tee /etc/systemd/system/gunicorn-$SITE_URL.service

sudo systemctl daemon-reload

sudo systemctl reload nginx

sudo systemctl enable gunicorn-$SITE_URL

sudo systemctl start gunicorn-$SITE_URL

```
