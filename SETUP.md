## Running locally
```
bash start-setup.sh
bash start-app.sh
```

First command sets up your DB, Queues, Caches. It runs under a different project namespace so as to not let docker clean up when running the second command.

Second command runs your application. It would first run __alembic__(database) migrations needed and then runs your application.
