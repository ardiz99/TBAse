# TBAse
This is a projected developed for Advanced Software Engeneering (290AA) course of Università degli Studi of Pisa. All the projected follows the principles of the course and shows the acquired capabilities about using softwares and frameworks as microFreshener, swagger, docker and postman, and knowledge about implementing a micro-services architecture.

The project was made by:
Ardizzoni Francesco, Del Castello Diego, Prestifilippo Colombrino Mattia, Tortorelli Felice.

# Get started
To correctly install and execute the application:
1) dowload it on your local device. You can do it by choicing between:
   - clicking on Code > Downlad ZIP 
   - excute on your prompt the command git clone https://github.com/ardiz99/TBAse.git
2) enter in the folder TBAse/src
3) run the command docker-compose up --build. If you don't have Docker installed you can download it from here https://www.docker.com/products/docker-desktop/
4) when the container are running, in another terminal (prompt command!! Powershell wouldn't work!) run the command docker exec -i db mysql -uroot -proot_password < ./db/ase.sql
5) try the APIs that you want. All the possible APIs are documented in the TBAse/doc folder, in OpenAPI files that you can import in swagger. To do this just open Swagger Editor (https://editor.swagger.io/) > File > Import File > select the .yaml file path that you'd like to see.
