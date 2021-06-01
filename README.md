# agencyGiuseppi
Spy agency admin tool

We’re building a simple tool for an international spy agency. The agency conducts
planned assassinations and has done so for decades. But it needs a new system
to assign assassinations (“hits”).

The general user is a hitman. He can be assigned a hit and see it on his list of
upcoming work. Typically, it succeeds and is closed out. But occasionally things
don’t work out and the target lives. In those cases, we assume the target hires
security and thus the case is forever closed, as a failed mission.
Like everyone else, hitmen have bosses. These are directly in charge of a group
of hitmen and can create hits and assign them. But they can only assign hits
to the hitmen they manage.

Finally, there’s the big boss of the agency - Giuseppi . He does not manage managers directly.
Rather, he just has free access to assign hits to anyone in the system. Even managers.
But when a new employee comes into the spy agency, he need not be added to The Boss’
list. It’s automatic.

The boss is also in charge of assigning hitmen to managers. Only he can do that.
For simplicity, the boss is always the first user in the database. No special
indications need to be added to flag the user as the boss.
Sadly, our hitmen do occasionally die in the field. Or worse, retire from the industry.
In this case, they can no longer be assigned hits and can no longer use the system.
Managers and The Boss can however, still check old assignments for these hitmen.

## Requirements:
* Mysql 8.0.x
* Python 3.8

## Install instruction
```bash
pip install -r requirements.txt
cp agencyGiuseppi/local_setting.ini agencyGiuseppi/local_setting.py
python manage.py migrate
python manage.py load_data 
```
Create and Env file in agencyGiuseppi folder
```bash
touch agencyGiuseppi/.env
```

Env Example:
```
DEBUG=true
DB_NAME=hitmen
DB_USERNAME=root
DB_PASSWORD=remote
DB_HOST=localhost
DB_PORT=3306
CURRENT_HOST=localhost
UPLOAD_MAX_SIZE=19
ADMIN_SITE_HEADER=Giuseppi
SENTRY_URL=
```

## Important information:
[Django environ doc](https://django-environ.readthedocs.io/en/latest/#tips)