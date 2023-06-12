from locust import HttpLocust, TaskSet, task, HttpUser
import json
import requests
import datetime

class UserActions(TaskSet):

    @task(1)
    def index5(self):
        self.client.get("/api/get_electronic_classifieds/")



class ApplicationUser(HttpUser):
    tasks = [UserActions]
    # min_wait = 5000
    # max_wait = 15000
    host = "https://jsonplaceholder.typicode.com"
    # stop_timeout = 200


# COMMAND for running locust
# locust --host='host_name'


# PORT for locust
# http://127.0.0.1:8089