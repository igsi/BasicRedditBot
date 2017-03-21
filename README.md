# Description

This is a program which monitors new submissions and comments in certain subreddits, stores the data in a Mongo DB and allows querying of the data using a simple GET request.

## Running the app using Docker
Use docker-compose, go to the root directory of this repository and run **sudo docker-compose up** to start everything.

###These are the 3 docker container to use:
    * The database is just a mongo:3.0 image from Docker Hub, no customization and no code required for this.
    * The reddit monitor uses the reddit API to listen for new submissions/commments.
    * The webserver
