from locust import HttpUser, task, between
import random

class GachaTestUser(HttpUser):
    wait_time = between(1, 2)  # Simula il tempo tra una richiesta e l'altra

    def on_start(self):
        """
        Eseguito all'inizio per ottenere il token di autorizzazione.
        """
        response = self.client.post(
            "/login_admin",
            json={"Email": "testadmin@example.com", "Password": "securepassword"},
            verify=False
        )
        if response.status_code == 200:
            self.token = response.json().get("data")  # Assume che il token sia nella chiave 'data'
            print("Access token ottenuto con successo.")
        else:
            self.token = None
            print(f"Errore durante l'ottenimento del token: {response.status_code}, {response.text}")

    @task(2)
    def add_gacha(self):
        """
        Task per aggiungere un nuovo gacha.
        """
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = self.client.post(
                "/gacha/add",
                json={
                    "Name": f"Gacha {random.randint(1, 1000)}",
                    "Description": "A new rare item",
                    "Status": "active"
                },
                headers=headers,
                name="Add Gacha"
            )
            print(f"Add Gacha: {response.status_code}")

    @task(2)
    def delete_gacha(self):
        """
        Task per rimuovere un gacha specifico.
        """
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            gacha_id = random.randint(1, 1000)  # ID casuale per simulare rimozione
            response = self.client.delete(
                f"/gacha/delete/{gacha_id}",
                headers=headers,
                name="Delete Gacha"
            )
            print(f"Delete Gacha: {response.status_code}")

    @task(2)
    def update_gacha_status(self):
        """
        Task per modificare lo stato di un gacha.
        """
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            gacha_id = random.randint(1, 1000)  # ID casuale per simulare modifica
            new_status = random.choice(["active", "inactive", "archived"])
            response = self.client.put(
                f"/gacha/update_status/{gacha_id}",
                json={"Status": new_status},
                headers=headers,
                name="Update Gacha Status"
            )
            print(f"Update Gacha Status: {response.status_code}")
    
    @task(2)
    def get_all_gachas(self):
        """
        Ottiene tutti i gacha disponibili.
        """
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = self.client.get("/gacha/get", headers=headers, verify=False)
            if response.status_code == 200:
                print("Richiesta di tutti i gachas riuscita.")
            else:
                print(f"Errore durante la richiesta di tutti i gachas: {response.status_code}, {response.text}")

    @task(2)
    def get_gacha_by_id(self):
        """
        Ottiene un gacha specifico tramite il suo ID.
        """
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = self.client.get("/gacha/get/1", headers=headers, verify=False)  # ID statico per il test
            if response.status_code == 200:
                print("Richiesta del gacha per ID riuscita.")
            else:
                print(f"Errore durante la richiesta del gacha per ID: {response.status_code}, {response.text}")

    @task(3)
    def get_gacha_by_name(self):
        """
        Ottiene un gacha specifico tramite il suo nome.
        """
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = self.client.get("/gacha/getName/bulbasaur", headers=headers, verify=False)  # Nome statico per il test
            if response.status_code == 200:
                print("Richiesta del gacha per nome riuscita.")
            else:
                print(f"Errore durante la richiesta del gacha per nome: {response.status_code}, {response.text}")


    # @task(3)
    # def update_gacha(self):
    #     # Update an existing Gacha entry
    #     gacha_id = random.randint(1, 100)  # Simulate existing Gacha ID
    #     if not self.token:
    #         print("Token missing. Skipping Gacha update.")
    #         return

    #     response = self.client.put(
    #         f"/update/{gacha_id}",
    #         json={
    #             "Name": f"Gacha-{random.randint(1, 10000)}-Updated",
    #             "Description": "Updated Gacha",
    #             "CurrencyCost": random.randint(1, 100)
    #         },
    #         headers={"Authorization": f"Bearer {self.token}"},
    #         name="Update Gacha",
    #         verify=False
    #     )
    #     if response.status_code == 200:
    #         print(f"Gacha {gacha_id} updated successfully")
    #     else:
    #         print(f"Failed to update Gacha {gacha_id}: {response.status_code}")

    @task(2)
    def delete_gacha(self):
        # Delete an existing Gacha entry
        gacha_id = random.randint(1, 100)  # Simulate existing Gacha ID
        if not self.token:
            print("Token missing. Skipping Gacha delete.")
            return

        response = self.client.delete(
            f"/delete/{gacha_id}",
            headers={"Authorization": f"Bearer {self.token}"},
            name="Delete Gacha",
            verify=False
        )
        if response.status_code == 200:
            print(f"Gacha {gacha_id} deleted successfully")
        else:
            print(f"Failed to delete Gacha {gacha_id}: {response.status_code}")

    # @task(2)
    # def get_gacha_by_id(self):
    #     # Get Gacha by ID
    #     gacha_id = random.randint(1, 100)  # Simulate existing Gacha ID
    #     if not self.token:
    #         print("Token missing. Skipping Gacha get by ID.")
    #         return

    #     response = self.client.get(
    #         f"/get/{gacha_id}",
    #         headers={"Authorization": f"Bearer {self.token}"},
    #         name="Get Gacha by ID",
    #         verify=False
    #     )
    #     if response.status_code == 200:
    #         print(f"Fetched Gacha {gacha_id} successfully")
    #     else:
    #         print(f"Failed to fetch Gacha {gacha_id}: {response.status_code}")

    # @task(2)
    # def get_gacha_by_name(self):
    #     # Get Gacha by Name
    #     gacha_name = f"Gacha-{random.randint(1, 10000)}"
    #     if not self.token:
    #         print("Token missing. Skipping Gacha get by name.")
    #         return

    #     response = self.client.get(
    #         f"/getName/{gacha_name}",
    #         headers={"Authorization": f"Bearer {self.token}"},
    #         name="Get Gacha by Name",
    #         verify=False
    #     )
    #     if response.status_code == 200:
    #         print(f"Fetched Gacha {gacha_name} successfully")
    #     else:
    #         print(f"Failed to fetch Gacha {gacha_name}: {response.status_code}")

    # @task(2)
    # def get_all_gachas(self):
    #     # Get all Gachas
    #     if not self.token:
    #         print("Token missing. Skipping Gacha get all.")
    #         return

    #     response = self.client.get(
    #         "/get",
    #         headers={"Authorization": f"Bearer {self.token}"},
    #         name="Get All Gachas",
    #         verify=False
    #     )
    #     if response.status_code == 200:
    #         print("Fetched all Gachas successfully")
    #     else:
    #         print(f"Failed to fetch all Gachas: {response.status_code}")

    # @task(1)
    # def get_my_gacha_by_id(self):
    #     # Get my Gacha by ID
    #     gacha_id = f"{random.randint(1, 100)}"
    #     if not self.token:
    #         print("Token missing. Skipping My Gacha get by ID.")
    #         return

    #     response = self.client.get(
    #         f"/mygacha/{gacha_id}",
    #         headers={"Authorization": f"Bearer {self.token}"},
    #         name="Get My Gacha by ID",
    #         verify=False
    #     )
    #     if response.status_code == 200:
    #         print(f"Fetched my Gacha {gacha_id} successfully")
    #     else:
    #         print(f"Failed to fetch my Gacha {gacha_id}: {response.status_code}")

    # @task(1)
    # def get_all_my_gachas(self):
    #     # Get all My Gachas
    #     if not self.token:
    #         print("Token missing. Skipping My Gacha get all.")
    #         return

    #     response = self.client.get(
    #         "/mygacha",
    #         headers={"Authorization": f"Bearer {self.token}"},
    #         name="Get All My Gachas",
    #         verify=False
    #     )
    #     if response.status_code == 200:
    #         print("Fetched all my Gachas successfully")
    #     else:
    #         print(f"Failed to fetch all my Gachas: {response.status_code}")