#!/bin/sh
if [ ! -d 'Node-Media-Server' ] then
termux-setup-storage;
pkg install python libjpeg-turbo libcrypt ndk-sysroot clang git ffmpeg nodejs -y;
LDFLAGS='-L/system/lib/' CFLAGS='-I/data/data/co.miescuela/files/usr/include/' pip install wheel pillow;
pip install 'django>=2.2' django-bootstrap-static django-koalalms-learning django-koalalms-accounts django-model-utils;
git -C $EXTERNAL_STORAGE clone https://github.com/dbcaturra/miescuela-koala.git;
cd $EXTERNAL_STORAGE/miescuela-koala && python manage.py migrate;
echo \"from accounts.models import Person\n Person.objects.create_superuser('admin', 'admin@miescuela.co', '!!password')\" | python manage.py shell;
git -C $EXTERNAL_STORAGE clone https://github.com/illuspas/Node-Media-Server;
cd $EXTERNAL_STORAGE/Node-Media-Server && npm i;
fi;
