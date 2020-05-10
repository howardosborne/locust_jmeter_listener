from locust import HttpUser, SequentialTaskSet, task, between
from plugins.jmeter_listener import JmeterListener
import json, random, string

#def print_url(r, *args, **kwargs):
#    print(r.url)

class MakePurchase(SequentialTaskSet):
    
    def on_start(self):
        #self.client.proxies = { "http"  : "http://localhost:8888", "https" : "https://localhost:8888"}
        #self.client.verify = False
        #self.client.hooks['response'].append(print_url)
        self.user_cookie = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + "-"
        self.user_cookie +=''.join(random.choices(string.ascii_lowercase + string.digits, k=4)) + "-"
        self.user_cookie +=''.join(random.choices(string.ascii_lowercase + string.digits, k=4)) + "-"
        self.user_cookie +=''.join(random.choices(string.ascii_lowercase + string.digits, k=4)) + "-"
        self.user_cookie +=''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        #self.user_cookie = "e5210750-97df-1064-d195-b1189a20add5"
        self.purchase_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + "-"
        self.purchase_id +=''.join(random.choices(string.ascii_lowercase + string.digits, k=4)) + "-"
        self.purchase_id +=''.join(random.choices(string.ascii_lowercase + string.digits, k=4)) + "-"
        self.purchase_id +=''.join(random.choices(string.ascii_lowercase + string.digits, k=4)) + "-"
        self.purchase_id +=''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        #self.purchase_id = "6aafb8ea-d35a-e9c7-b4ff-7cc1efa2b217"

    @task
    def home(self):
        self.client.get("/", name ="01 /")

    @task
    def get_config_json(self):
        response = self.client.get("/config.json", name="02 /config.json")
        response_json = json.loads(response.text)
        self.api_host = response_json["API_URL"]

    @task
    def third_task(self):
        response = self.client.get(self.api_host + "/entries", name="03 /entries")
        response_json = json.loads(response.text)
        self.id = response_json["Items"][0]["id"]

    @task
    def fourth_task(self):
        self.client.cookies["user"] = self.user_cookie
        response = self.client.get("/prod.html?idp_=" + str(self.id), name="04 /prod.html?idp_")

    @task
    def fifth_task(self):
        payload = '{"id":"' + str(self.id) + '"}'
        response = self.client.post(self.api_host + "/view", payload , headers={"Content-Type": "application/json"}, name="05 /view")

    @task
    def sixth_task(self):
        payload = '{"id":"' + self.purchase_id + '","cookie":"user=' + self.user_cookie + '","prod_id":' + str(self.id) + ',"flag":false}'
        response = self.client.post(self.api_host + "/addtocart", payload, headers={"Content-Type": "application/json"},  name="06 /addtocart")

    @task
    def seventh_task(self):
        response = self.client.get("/cart.html", name="07 /cart.html")

    @task
    def eighth_task(self):
        payload = '{"cookie":"user=' + self.user_cookie + '","flag":false}'
        response = self.client.post(self.api_host + "/viewcart", payload, headers={"Content-Type": "application/json"},  name="08 /viewcart")

    @task
    def ninth_task(self):
        payload = '{"cookie":"user=' + self.user_cookie + '"}'
        response = self.client.post(self.api_host + "/deletecart", payload, headers={"Content-Type": "application/json"},  name="09 /deletecart")


class WebsiteUser(HttpUser):
    """
    User class that does requests to the locust web server running on localhost
    """
    host = "https://www.demoblaze.com"
    wait_time = between(2, 5)
    tasks = [MakePurchase]

    def on_start(self):
        jmeter_listener.add_user()
        jmeter_listener.set_user_name(self.__class__.__name__)

jmeter_listener = JmeterListener()