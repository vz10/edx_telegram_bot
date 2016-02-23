This is telegram bot for edx clients support
======================================================================
Run following commands:

```
cd /edx/app/edxapp/edx-platform/
git clone https://github.com/vz10/raccoonBot.git
mv raccoonBot edx_telegram_bot
pip install -e edx_telegram_bot
```

In `lms/envs/common.py` add:

```
ROOT_URLCONF = 'edx_telegram_bot.urls'
...
INSTALLED_APPS = {
    ...
    'edx_telegram_bot',
    ...
}
...
MAKO_TEMPLATES['main'] = ['/edx/app/edxapp/edx-platform/edx-telegram-bot/edx_telegram_bot/templates/lms'] + \
                         MAKO_TEMPLATES['main']
...
```
To start bot use this command in parallel terminal after starting LMS

```
./manage.py lms start_bot --settings=devstack
```
