# Restoring to a Heroku Postgres instance
If you are using Heroku to host your application, you will need to upload the backup file and restore it to your Postgres add-on.

*Note: This assumes that you have previously linked your local repository to your Heroku instance using Heroku Toolbelt and that you already have a Heroku Postgres add-on attached.*

1. You will first need to make the .dump file available for download via a URL using something like Amazon S3.

2. In a terminal navigate to your local repo

3. Run the following command replacing *<heroku_app_name>* with the name of your heroku app and the URL with the URL of your .dump file:

```bash
$ heroku pg:backups restore -a <heroku_app_name> 'https://url.to/openods.dump' DATABASE_URL
```

4. I'd then recommend doing a `heroku -a <heroku_app_name> restart` which will cycle your dynos
