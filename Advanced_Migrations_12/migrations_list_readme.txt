Basic commands
---------------------------------
python manage.py makemigrations
python manage.py migrate

python manage.py makemigrations <app name>
python manage.py migrate <app name>

New commands
--------------------------------
python .\manage.py makemigrations shop --empty --name uppercase_name
python manage.py migrate books 0002 # reversing commands
python manage.py migrate books zero # reverse all makemigrations
python manage.py showmigrations
python manage.py sqlmigrate 0002
python manage.py makemigrations --check --dry-run # it only checks whether the migration files were created




link
------------------------------------------------
https://docs.djangoproject.com/en/5.2/ref/migration-operations/
https://docs.djangoproject.com/en/5.2/topics/migrations/



