# Twitter-Memories-Backend
Repository for the Twitter Memories project, a web app that allows users to look back on past tweets they have posted on the same day. Front end code is found [here](https://github.com/Gustavo-Cornejo/Twitter-Memories-Frontend)


## Main Components
* ### Flask Web Server
    - Serves the Flask API that both the Celery Worker Server and the VueJS web app communicate with.
    - (LATER ADDING ENDPOINT DOCUMENTATION w/SWAGGER)
* ### Celery Worker Server
    - Called the processingEngine, this component handles the processing done to the raw CSV user Twitter Archives.
* ### RabbitMQ via [CloudAMPQ](https://www.cloudamqp.com/)
    - The Flask Web Server pushes to this job queue while the celery worker server grabs jobs from here.  
* ### ControllerDB/MongoDB via [mLab](https://mlab.com/)
    - Stores user data, including collections of tweet ids. Used by both the web server and the worker server via controllerDB module. 
* ### Frontend VueJS app
    - Web app deployed on Firebase 

## How to run locally (coming soon)