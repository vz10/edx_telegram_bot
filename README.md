This is telegram bot for edx clients support
======================================================================
Connect to vagrant via ssh. By user **edxapp** run following commands:

```
cd /edx/app/edxapp/edx-platform/
git clone https://github.com/vz10/edx_telegram_bot.git
pip install -e edx_telegram_bot
```

In `lms/urls.py` :

- add to the end of file

    ```
    ...
    urlpatterns += (
        url(r'^bot/', include('edx_telegram_bot.edx_telegram_bot.urls')),
    )
    ...
    ```

In `lms/envs/common.py` :

- add telegram bot to installed application list

    ```
    ...
    INSTALLED_APPS = {
        ...
        'edx_telegram_bot.edx_telegram_bot',
        ...
    }
    ...
    ```
- override default student profile template 
    ```
    ...
    
    MAKO_TEMPLATES['main'] = ['/edx/app/edxapp/edx-platform/edx_telegram_bot/edx_telegram_bot/templates/lms'] + \
                             MAKO_TEMPLATES['main']
    ...
    ```

- Add bot settings (https://core.telegram.org/bots#3-how-do-i-create-a-bot)
    - token - bot token recieved by BotFather bot. 
    - bot_name - your bot username
    ```
    ...
    TELEGRAM_BOT = {
        'token': '<TELEGRAM_BOT_TOKEN>',
        'bot_name': "<TELEGRAM_BOT_USERNAME>"
    }
    ...
    ```
    
In `cms/envs/common.py` :

- override default course page template 
    ```
    ...
    
    MAKO_TEMPLATES['main'] = ['/edx/app/edxapp/edx-platform/edx_telegram_bot/edx_telegram_bot/templates/cms'] + \
                             MAKO_TEMPLATES['main']
    ...
    ```
Use this command to start bot  in parallel terminal after starting LMS
```
./manage.py lms start_bot --settings=devstack
```
