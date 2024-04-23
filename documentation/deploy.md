# Deloying

## Versioning

We are using [https://semver.org/](semver) for versioning. We have three branches main, staging and prod. We will create a new release branch from main branch for each new release. The release branch will be merged to staging and prod branch after testing.

## Staging

Create new release in github from main branch. Then merge the release branch to stating. Now docker ci will build the image and push it to the docker hub.
In statig server there is [https://containrrr.dev/watchtower/](watchtower) running which will pull the latest image and run it. 

## Production

Use the same process as stating but merge the release branch to production. In production server there is [https://containrrr.dev/watchtower/](watchtower) running which will pull the latest image and run it.

## Rollback

If there is any issue with the new release, you can rollback to the previous release by merging the previous release branch to the production or stating branch.

## Monitoring

You can monitor the logs of the running container by login to staging or production server and running the following command.

```bash
ssh ubuntu@staging.mammalbase.net -i mammalbase-staging-key.pem
```
You can get password and key from kari

### Seeing logs

```bash
sudo docker ps

# Get the container id from the above command and run the following command

sudo docker logs <container_id>
```

### Restarting the container

```bash
sudo docker ps

# Get the container id from the above command and run the following command

sudo docker restart <container_id>
```

## Errors

If there is any error in the container, you can see the logs and fix the issue. If you are not able to fix the issue, you can rollback to the previous release.

**Sometimes restarting the nginx server will fix the issue. You can restart the nginx server by running the following command.**

```bash
sudo docker restart <container_id>
```

