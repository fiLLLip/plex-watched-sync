# Plex Watched Sync
Synchronize watched status between Plex Media Servers. Ready to use! Very convenient if you have access to several Plex Media Servers and use wathed status actively to track your tv-series progress. Already have an instance of the server running, to ease use. See detailed desciption.

This is my first Python project, so be nice :)
 
###Collaboration
Feel free to contribute!

###Roadmap
- [x] ~~Frontend to ease authentication between account and plex.tv~~
- [ ] Deploy server on cloud VPS
- [ ] Refactor

###License
   Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
   
   Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License. 

##Server
The server application is based on Falcon web framework ( https://falconframework.org/ ), and running with Redis as the datastore.

###Requirements
* Python >=2.7
* Redis
* Requests
* Falcon
* Gunicorn (or another server for running Falcon)

###Installation
```pip install redis requests falcon gunicorn gevent```

If Redis is installed and running, you can run the server when located in the server folder with ```gunicorn --bind 0.0.0.0:8000 serve:app```

###Security
For your server to get access to an accounts watched status, the account owner must allow it to do so. In the ```frontend```-folder there is an AngularJS app to easily let your users do this (you must edit the server url in ```controllers.js```.
If you are using the running instance on http://plexsync.filllip.net:8080/api/, you can direct your users to the following url: http://plexsync.filllip.net:8080/ 

**For the advanced user**
There is an endpoint to "log in" with a plex user account, to add it to the system and authorize server access to it. 
First, you need to get an authorization token from plex. You can do that by editing the username and password and running this cURL:
```
curl -X POST -H "X-Plex-Product: WatchStateSync" -H "X-Plex-Version: 0.1" -H "X-Plex-Client-Identifier: WatchStateSync" -H "Cache-Control: no-cache" -H "Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW" -F "user[login]=<username>" -F "user[password]=<password>" "https://plex.tv/users/sign_in.json"
```
From the response, copy the authorizationToken and use it in the following cURL:
```
curl -X POST -H "X-token: <token>" -H "Cache-Control: no-cache" "http://plexsync.filllip.net:8080/api/user/login"
```
Now your user is added to the system and all servers you have access to is authorized to read and update your watched data.

##Client
Runs on the same machine as the Plex Media Server. Copy the props.py.sample and rename to props.py. Invoke the script via a cron job. Every minute is often enough.
###Config
**BASE_URL**
Server url without trailing slash. There is already an instance running at http://plexsync.filllip.net:8080/api/. Feel free to use.

**SERVER_ID**
Log into plex.tv and find "machineIdentifier" for your server at https://plex.tv/pms/servers.xml

**DB_PATH**
Path to Plex DB

**ADMIN_ACCOUNT_REAL_ID**
In local Plex DB the admins account ID is 1 (most likely your account). Log into plex.tv and find your account ID at https://plex.tv/users/account

###Requirements
* Python >=2.7
* SQLite3
* Requests

###Installation
```pip install requests sqlite3```

Set up the property file, then add to crontab:
```
*/30 * * * * /usr/bin/python /root/plex-watched-sync/client/sync.py > /var/log/plexsync-cron.log
```
Now wait and enjoy.
