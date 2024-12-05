from locust import HttpUser, task, between

class APITestUser(HttpUser):
    wait_time = between(1, 5)  # Tempo di attesa tra le richieste

    def headers(self):
        # Aggiungi qui un token di autorizzazione se necessario
        return {"Authorization": "Bearer <your_token>"}

    @task
    def login(self):
        self.client.get(
            "/login",
            params={"Email": "test@example.com", "Password": "password123"},
            name="Login User (Auth Service)",
            verify=False  # Ignora la verifica SSL
        )

    @task
    def register(self):
        self.client.post(
            "/register",
            json={
                "FirstName": "Test",
                "LastName": "User",
                "Email": "test@example.com",
                "Password": "password123",
                "CurrencyAmount": 100
            },
            name="Register User (Auth Service)",
            verify=False  # Ignora la verifica SSL
        )

    @task
    def get_all_gachas(self):
        self.client.get(
            "/gacha/get",
            headers=self.headers(),
            name="Get All Gachas (Gacha Service)",
            verify=False  # Ignora la verifica SSL
        )

    @task
    def get_all_auctions(self):
        self.client.get(
            "/auction",
            headers=self.headers(),
            name="Get All Auctions (Market Service)",
            verify=False  # Ignora la verifica SSL
        )

    @task
    def buy_currency(self):
        self.client.put(
            "/buy_currency",
            headers=self.headers(),
            json={"quantity": 10},
            name="Buy Currency (Currency Service)",
            verify=False  # Ignora la verifica SSL
        )

    @task
    def bid_on_auction(self):
        self.client.put(
            "/bid/1",
            headers=self.headers(),
            json={"bid": 150},
            name="Bid on Auction (Market Service)",
            verify=False  # Ignora la verifica SSL
        )

    @task
    def transaction_history(self):
        self.client.get(
            "/my_transaction_history",
            headers=self.headers(),
            name="Transaction History (Market Service)",
            verify=False  # Ignora la verifica SSL
        )

    @task
    def roll(self):
        self.client.get(
            "/roll",
            headers=self.headers(),
            name="Roll (Currency Service)",
            verify=False  # Ignora la verifica SSL
        )

    @task
    def golden_roll(self):
        self.client.get(
            "/golden_roll",
            headers=self.headers(),
            name="Golden Roll (Currency Service)",
            verify=False  # Ignora la verifica SSL
        )
