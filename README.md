This is telegram bot for edx clients support
======================================================================
Run following commands:

```
cd /edx/app/edxapp/edx-platform/
git clone https://github.com/vz10/raccoonBot.git
mv raccoonBot edx-telegram-bot
pip install -e edx-telegram-bot
```

In `lms/envs/common.py` add:

```
...
INSTALLED_APPS = {
    ...
    'edx-telegram-bot',
    ...
}
...
MAKO_TEMPLATES['main'] = ['/edx/app/edxapp/edx-platform/edx-telegram-bot/edx-telegram-bot/templates/lms'] + \
                         MAKO_TEMPLATES['main']
...
```
