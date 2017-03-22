# Description

This is a program which monitors new submissions and comments in certain subreddits, stores the data in a Mongo DB and allows querying of the data using a simple GET request.
The subreddits to monitor are specified in the file configuration.json by providing a list with the key "subreddits".

## Running the app using Docker
Use docker-compose, go to the root directory of this repository and run **sudo docker-compose up** to start everything.

### Docker containers
This project uses 3 docker images, these contain:
* A database which is just a mongo:3.0 image from Docker Hub, no customization and no code required for this. The actual data stored in the database is mapped to a location outside the container: <repo>/data/ .
* A reddit monitor which uses the reddit API to listen for new submissions/commments.
* A webserver which exposes two GET endpoints to access the data stored in the DB.
    
### Usage
* The reddit container continuously listens for new submissions/comments and inserts them in the DB. It does not accept any outside commands.
* In order to connect to the DB using the mongo client use port **5000** and localhost.
* The webserver exposes two **GET** endpoints:
  * **/all** which lists all items in the DB
  * **/items?subreddit=<subreddit>&from=<t1>&to=<t2>&keyword=<kw>** where:
    * *subreddit* is the subreddit name (e.g. for https://www.reddit.com/r/python the subreddit is python)
    * *from* and *to* areUNIX timestamps that define the time frame range
    * *keyword* is optional and it allows for an exact word search in the content field of items stored in the DB. The search is case-insensitive.

### Configuration
The program is configured through the file **configuration.json**. It has 4 sections:
* **subbredits** mandatory sections which contains the list of subreddits to monitor.
* **database** it contains details on how to connect to the Mongo DB instance. It does not have an effect on the DB instance itself.
* **reddit** client details for using the reddit API.
* **webserver** sets the server configuration.
