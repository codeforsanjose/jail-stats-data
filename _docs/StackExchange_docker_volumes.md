I have a Python app using a SQLite database (it's a data collector that runs daily by cron).  I want to deploy it, probably on AWS or Google Container Engine, using Docker.  I see three main steps:  
1. Containerize and test the app locally.  
2. Deploy and run the app on AWS or GCE.  
3. Backup the DB periodically and download back to a local archive.  

Recent posts (on Docker, [StackOverflow](http://stackoverflow.com/questions/18496940/how-to-deal-with-persistent-storage-e-g-databases-in-docker) and elsewhere) say that since 1.9, Volumes are now the recommended way to handle persisted data, rather than the "data container" pattern.  For future compatibility, I always like to use the preferred, idiomatic method, however Volumes seem to be much more of a challenge than data containers.  Am I missing something??

Following the "data container" pattern, I can easily:

* Build a base image with all the static program and config files.
* From that image create a data container image and copy my DB and backup directory into it (simple COPY in the Dockerfile).
* Push both images to Docker Hub.
* Pull them down to AWS.
* Run the data and base images, using "--volume-from" to refer to the data.

Using "docker volume create":

* I'm unclear how to copy my DB into the volume.
* I'm very unclear how to get that volume (containing the DB) up to AWS or GCE... you can't PUSH/PULL a volume.

Am I missing something regarding Volumes?  
Is there a good overview of using Volumes to do what I want to do?  
Is there a recommended, idiomatic way to backup and download data (either using the data container pattern or volumes) as per my step 3?





