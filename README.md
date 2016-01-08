# flask-rethinkdb-chat
Of all the example projects on the rethinkdb site (https://www.rethinkdb.com/docs/examples/) the only one that showed a good use case of changefeeds was the CatThink project (https://www.rethinkdb.com/blog/cats-of-instagram/) which was written in JavaScript. There are some good example python projects but no one is using a changefeed in the python projects. I wanted to see if I could make a nice chat app with python socket-io and of course rethinkdb. This is the result.

The project has been set up to work with docker/docker-compose so in order to run the project just run `docker-compose build` then `docker-compose up`. You will notice an error from the web container. Just open a shell in the container and open up the python terminal from there and run: `from main import init_db` and then `init_db()`. Restart the containers and then you should be good to go!


Demo:

![](https://cloud.githubusercontent.com/assets/2521298/12210674/f3fcfde2-b618-11e5-99f2-57c3fa857f3b.gif)
