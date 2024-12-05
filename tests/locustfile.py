from locust import HttpUser, task, between
import random

class APITestUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Inizializzazione prima dell'esecuzione dei task."""
        self.email = f"user{random.randint(1, 10000)}@example.com"
        self.password = "password123"
        self.is_admin = random.choice([True, False])  # 50% chance di essere admin
        self.token = None
        
        self.register_user()
        self.login_user()

    @task(2)
    def register_user(self):
        """Registra un nuovo utente."""
        response = self.client.post(
            "/register",
            json={
                "FirstName": "Test",
                "LastName": "User",
                "Email": self.email,
                "Password": self.password,
                "CurrencyAmount": 100
            },
            name="Register User",
            verify=False
        )
        if response.status_code == 200:
            print(f"User {self.email} registered successfully.")
        else:
            print(f"User registration failed: {response.status_code}")

    @task(2)
    def login_user(self):
        """Effettua il login per un utente."""
        response = self.client.get(
            "/login",
            params={"Email": self.email, "Password": self.password},
            name="Login User",
            verify=False
        )
        if response.status_code == 200:
            self.token = response.json().get("data")
            print(f"User {self.email} logged in successfully.")
        else:
            print(f"User login failed: {response.status_code}")

    @task(3)
    def get_all_auctions(self):
        """Ottieni tutte le aste."""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get(
            "/auction",
            headers=headers,
            name="Get All Auctions",
            verify=False
        )
        if response.status_code == 200:
            print("Fetched all auctions.")
        elif response.status_code == 401:
            print("Unauthorized access to auctions.")

    @task(3)
    def roll(self):
        """Effettua un roll."""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get(
            "/roll",
            headers=headers,
            name="Roll",
            verify=False
        )
        if response.status_code == 200:
            print("Roll executed successfully.")
        elif response.status_code == 401:
            print("Unauthorized roll attempt.")

    @task(1)
    def buy_currency(self):
        """Compra una quantità di valuta."""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.put(
            "/buy_currency",
            json={"quantity": 50},
            headers=headers,
            name="Buy Currency",
            verify=False
        )
        if response.status_code == 200:
            print("Currency bought successfully.")
        elif response.status_code == 401:
            print("Unauthorized currency purchase attempt.")

    @task(2)
    def get_transaction_history(self):
        """Ottieni la cronologia delle transazioni."""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get(
            "/my_transaction_history",
            headers=headers,
            name="Transaction History",
            verify=False
        )
        if response.status_code == 200:
            print("Transaction history retrieved successfully.")
        elif response.status_code == 401:
            print("Unauthorized access to transaction history.")

    @task(1)
    def new_auction(self):
        """Crea una nuova asta."""
        if not self.is_admin:  # Solo gli admin possono creare aste
            return
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.post(
            "/new_auction",
            json={
                "gacha_id": random.randint(1, 100),
                "starting_price": random.randint(100, 1000),
                "end_date": "2024-12-31 23:59:59"
            },
            headers=headers,
            name="New Auction",
            verify=False
        )
        if response.status_code == 200:
            print("New auction created successfully.")
        elif response.status_code == 401:
            print("Unauthorized auction creation attempt.")