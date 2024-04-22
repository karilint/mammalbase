# Deloying

## Versioning

We are using [semver](https://semver.org/) for versioning. We have three branches main, staging and prod. We will create a new release branch from main branch for each new release. The release branch will be merged to staging and prod branch after testing.

## Staging

https://staging.mammalbase.net/

Create new release in github from main branch. Then merge the release branch to `staging`. Now github ci will build the image and push it to the docker hub.

In statig server there is [watchtower](https://containrrr.dev/watchtower/) running which will pull the latest image and restart the container and database.

## Production

https://www.mammalbase.net/

Use the same process as stating but merge the release branch to `prod`. In production server there is [watchtower](https://containrrr.dev/watchtower/) running which will pull the latest image and restart the container and database.

## Rollback

If there is any issue with the new release, you can rollback to the previous release by merging the previous release branch to the production or staging branch.

## SSH

You can monitor the logs of the running container by login to staging or production server and running the following command.

```bash
ssh ubuntu@*staging*.mammalbase.net -i mammalbase-staging-key.pem
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
sudo docker restart <nginx_container_id>
```

