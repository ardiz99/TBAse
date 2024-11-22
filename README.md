# TBAse  
This project was developed for the Advanced Software Engineering (290AA) course at the Università degli Studi di Pisa. The entire project adheres to the principles taught during the course and demonstrates the acquired skills in using tools and frameworks such as microFreshener, Swagger, Docker, and Postman, as well as knowledge of implementing a microservices architecture.  

The project was created by:  
Ardizzoni Francesco, Del Castello Diego, Prestifilippo Colombrino Mattia, Tortorelli Felice.  

---

# Get Started  

To install and run the application correctly, follow these steps:  

1. **Download the project** to your local device. You can do this by:  
   - Clicking on `Code > Download ZIP`  
   - Executing the following command in your terminal:  
     ```bash  
     git clone https://github.com/ardiz99/TBAse.git  
     ```  

2. Navigate to the `TBAse/src` folder.  

3. Run the command:  
   ```bash  
   docker-compose up --build  
   ```  
   If you don’t have Docker installed, you can download it from here https://www.docker.com/products/docker-desktop/

4. Once the containers are running, open another terminal (ensure it’s the Command Prompt, as PowerShell may not work) and execute the following command to initialize the database:
   ```bash  
   docker exec -i db mysql -uroot -proot_password < ./db/ase.sql 
   ```
   
5. Test the APIs you need. All available APIs are documented in the TBAse/doc folder as OpenAPI files. You can import these into Swagger to explore them:
   - Open Swagger Editor.
   - Go to File > Import File.
   - Select the .yaml file corresponding to the API you want to test.
