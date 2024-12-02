CREATE DATABASE  IF NOT EXISTS `ase` /*!40100 DEFAULT CHARACTER SET utf8mb3 */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `ase`;
-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: ase
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `UserID` int NOT NULL AUTO_INCREMENT,
  `FirstName` varchar(45) NOT NULL,
  `LastName` varchar(45) NOT NULL,
  `Password` varchar(45) NOT NULL,
  `Email` varchar(45) NOT NULL,
  PRIMARY KEY (`UserID`),
  UNIQUE KEY `Email_UNIQUE` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (1,'Diego','Del Castello','a','a'),(2,'Felice','Tortorelli','s','s'),(3,'Francesco','Ardizzoni','z','z'),(4,'Mattia','Prestifilippo','x','x');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gacha`
--

DROP TABLE IF EXISTS `gacha`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gacha` (
  `GachaId` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(45) NOT NULL,
  `Type1` varchar(45) NOT NULL,
  `Type2` varchar(45) NOT NULL,
  `Total` int NOT NULL,
  `HP` int NOT NULL,
  `Attack` int NOT NULL,
  `Defense` int NOT NULL,
  `SpAtt` int NOT NULL,
  `SpDef` int NOT NULL,
  `Speed` int NOT NULL,
  `Rarity` varchar(45) NOT NULL,
  `Link` varchar(45) NOT NULL,
  PRIMARY KEY (`GachaId`)
) ENGINE=InnoDB AUTO_INCREMENT=152 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gacha`
--

LOCK TABLES `gacha` WRITE;
/*!40000 ALTER TABLE `gacha` DISABLE KEYS */;
INSERT INTO `gacha` VALUES (1,'Bulbasaur','Grass','Poison',318,45,49,49,65,65,45,'Uncommon','/img/bulbasaur.png'),(2,'Ivysaur','Grass','Poison',405,60,62,63,80,80,60,'Rare','/img/ivysaur.png'),(3,'Venusaur','Grass','Poison',525,80,82,83,100,100,80,'Epic','/img/venusaur.png'),(4,'Charmander','Fire','',309,39,52,43,60,50,65,'Uncommon','/img/charmander.png'),(5,'Charmeleon','Fire','',405,58,64,58,80,65,80,'Rare','/img/charmeleon.png'),(6,'Charizard','Fire','Flying',534,78,84,78,109,85,100,'Epic','/img/charizard.png'),(7,'Squirtle','Water','',314,44,48,65,50,64,43,'Uncommon','/img/squirtle.png'),(8,'Wartortle','Water','',405,59,63,80,65,80,58,'Rare','/img/wartortle.png'),(9,'Blastoise','Water','',530,79,83,100,85,105,78,'Epic','/img/blastoise.png'),(10,'Caterpie','Bug','',195,45,30,35,20,20,45,'Common','/img/caterpie.png'),(11,'Metapod','Bug','',205,50,20,55,25,25,30,'Common','/img/metapod.png'),(12,'Butterfree','Bug','Flying',395,60,45,50,90,80,70,'Uncommon','/img/butterfree.png'),(13,'Weedle','Bug','Poison',195,40,35,30,20,20,50,'Common','/img/weedle.png'),(14,'Kakuna','Bug','Poison',205,45,25,50,25,25,35,'Common','/img/kakuna.png'),(15,'Beedrill','Bug','Poison',395,65,90,40,45,80,75,'Uncommon','/img/beedrill.png'),(16,'Pidgey','Normal','Flying',251,40,45,40,35,35,56,'Common','/img/pidgey.png'),(17,'Pidgeotto','Normal','Flying',349,63,60,55,50,50,71,'Uncommon','/img/pidgeotto.png'),(18,'Pidgeot','Normal','Flying',479,83,80,75,70,70,101,'Rare','/img/pidgeot.png'),(19,'Rattata','Normal','',253,30,56,35,25,35,72,'Common','/img/rattata.png'),(20,'Raticate','Normal','',413,55,81,60,50,70,97,'Uncommon','/img/raticate.png'),(21,'Spearow','Normal','Flying',262,40,60,30,31,31,70,'Common','/img/spearow.png'),(22,'Fearow','Normal','Flying',442,65,90,65,61,61,100,'Uncommon','/img/fearow.png'),(23,'Ekans','Poison','',288,35,60,44,40,54,55,'Common','/img/ekans.png'),(24,'Arbok','Poison','',438,60,85,69,65,79,80,'Uncommon','/img/arbok.png'),(25,'Pikachu','Electric','',320,35,55,40,50,50,90,'Uncommon','/img/pikachu.png'),(26,'Raichu','Electric','',485,60,90,55,90,80,110,'Rare','/img/raichu.png'),(27,'Sandshrew','Ground','',300,50,75,85,20,30,40,'Common','/img/sandshrew.png'),(28,'Sandslash','Ground','',450,75,100,110,45,55,65,'Uncommon','/img/sandslash.png'),(29,'Nidoran F','Poison','',275,55,47,52,40,40,41,'Common','/img/nidoran-f.png'),(30,'Nidorina','Poison','',365,70,62,67,55,55,56,'Uncommon','/img/nidorina.png'),(31,'Nidoqueen','Poison','Ground',505,90,92,87,75,85,76,'Epic','/img/nidoqueen.png'),(32,'Nidoran M','Poison','',273,46,57,40,40,40,50,'Common','/img/nidoran-m.png'),(33,'Nidorino','Poison','',365,61,72,57,55,55,65,'Uncommon','/img/nidorino.png'),(34,'Nidoking','Poison','Ground',505,81,102,77,85,75,85,'Epic','/img/nidoking.png'),(35,'Clefairy','Fairy','',323,70,45,48,60,65,35,'Common','/img/clefairy.png'),(36,'Clefable','Fairy','',483,95,70,73,95,90,60,'Rare','/img/clefable.png'),(37,'Vulpix','Fire','',299,38,41,40,50,65,65,'Common','/img/vulpix.png'),(38,'Ninetales','Fire','',495,73,76,75,81,95,95,'Rare','/img/ninetales.png'),(39,'Jigglypuff','Normal','Fairy',270,115,45,20,45,25,20,'Common','/img/jigglypuff.png'),(40,'Wigglytuff','Normal','Fairy',435,140,70,45,85,50,45,'Uncommon','/img/wigglytuff.png'),(41,'Zubat','Poison','Flying',245,40,45,35,30,40,55,'Common','/img/zubat.png'),(42,'Golbat','Poison','Flying',455,75,80,70,65,75,90,'Uncommon','/img/golbat.png'),(43,'Oddish','Grass','Poison',320,45,50,55,75,65,30,'Common','/img/oddish.png'),(44,'Gloom','Grass','Poison',395,60,65,70,85,75,40,'Uncommon','/img/gloom.png'),(45,'Vileplume','Grass','Poison',490,75,80,85,110,90,50,'Rare','/img/vileplume.png'),(46,'Paras','Bug','Grass',285,35,70,55,45,55,25,'Common','/img/paras.png'),(47,'Parasect','Bug','Grass',405,60,95,80,60,80,30,'Uncommon','/img/parasect.png'),(48,'Venonat','Bug','Poison',305,60,55,50,40,55,45,'Common','/img/venonat.png'),(49,'Venomoth','Bug','Poison',450,70,65,60,90,75,90,'Rare','/img/venomoth.png'),(50,'Diglett','Ground','',265,10,55,25,35,45,95,'Common','/img/diglett.png'),(51,'Dugtrio','Ground','',405,35,80,50,50,70,120,'Uncommon','/img/dugtrio.png'),(52,'Meowth','Normal','',290,40,45,35,40,40,90,'Common','/img/meowth.png'),(53,'Persian','Normal','',440,65,70,60,65,65,115,'Uncommon','/img/persian.png'),(54,'Psyduck','Water','',320,50,52,48,65,50,55,'Common','/img/psyduck.png'),(55,'Golduck','Water','',495,80,82,78,90,80,85,'Rare','/img/golduck.png'),(56,'Mankey','Fighting','',305,40,80,35,35,45,70,'Common','/img/mankey.png'),(57,'Primeape','Fighting','',455,65,105,60,60,70,95,'Rare','/img/primeape.png'),(58,'Growlithe','Fire','',350,55,70,45,70,50,60,'Uncommon','/img/growlithe.png'),(59,'Arcanine','Fire','',555,90,110,80,100,80,95,'Epic','/img/arcanine.png'),(60,'Poliwag','Water','',300,40,50,40,40,40,90,'Common','/img/poliwag.png'),(61,'Poliwhirl','Water','',385,65,65,65,50,50,90,'Uncommon','/img/poliwhirl.png'),(62,'Poliwrath','Water','Fighting',510,90,95,95,70,90,70,'Epic','/img/poliwrath.png'),(63,'Abra','Psychic','',310,25,20,15,105,55,90,'Common','/img/abra.png'),(64,'Kadabra','Psychic','',400,40,35,30,120,70,105,'Rare','/img/kadabra.png'),(65,'Alakazam','Psychic','',500,55,50,45,135,95,120,'Epic','/img/alakazam.png'),(66,'Machop','Fighting','',305,70,80,50,35,35,35,'Common','/img/machop.png'),(67,'Machoke','Fighting','',405,80,100,70,50,60,45,'Uncommon','/img/machoke.png'),(68,'Machamp','Fighting','',505,90,130,80,65,85,55,'Epic','/img/machamp.png'),(69,'Bellsprout','Grass','Poison',300,50,75,35,70,30,40,'Common','/img/bellsprout.png'),(70,'Weepinbell','Grass','Poison',390,65,90,50,85,45,55,'Uncommon','/img/weepinbell.png'),(71,'Victreebel','Grass','Poison',490,80,105,65,100,70,70,'Rare','/img/victreebel.png'),(72,'Tentacool','Water','Poison',335,40,40,35,50,100,70,'Common','/img/tentacool.png'),(73,'Tentacruel','Water','Poison',515,80,70,65,80,120,100,'Epic','/img/tentacruel.png'),(74,'Geodude','Rock','Ground',300,40,80,100,30,30,20,'Common','/img/geodude.png'),(75,'Graveler','Rock','Ground',390,55,95,115,45,45,35,'Uncommon','/img/graveler.png'),(76,'Golem','Rock','Ground',495,80,120,130,55,65,45,'Rare','/img/golem.png'),(77,'Ponyta','Fire','',410,50,85,55,65,65,90,'Uncommon','/img/ponyta.png'),(78,'Rapidash','Fire','',495,60,100,70,80,80,105,'Rare','/img/rapidash.png'),(79,'Slowpoke','Water','Psychic',315,90,65,65,40,40,15,'Common','/img/slowpoke.png'),(80,'Slowbro','Water','Psychic',490,95,75,110,100,80,30,'Rare','/img/slowbro.png'),(81,'Magnemite','Electric','Steel',325,25,35,70,95,55,45,'Common','/img/magnemite.png'),(82,'Magneton','Electric','Steel',465,50,60,95,120,70,70,'Uncommon','/img/magneton.png'),(83,'Farfetch\'d','Normal','Flying',352,52,65,55,58,62,60,'Uncommon','/img/farfetchd.png'),(84,'Doduo','Normal','Flying',310,35,85,45,35,35,75,'Common','/img/doduo.png'),(85,'Dodrio','Normal','Flying',460,60,110,70,60,60,100,'Uncommon','/img/dodrio.png'),(86,'Seel','Water','',325,65,45,55,45,70,45,'Common','/img/seel.png'),(87,'Dewgong','Water','Ice',475,90,70,80,70,95,70,'Rare','/img/dewgong.png'),(88,'Grimer','Poison','',325,80,80,50,40,50,25,'Common','/img/grimer.png'),(89,'Muk','Poison','',495,100,105,75,65,100,50,'Rare','/img/muk.png'),(90,'Shellder','Water','',305,30,65,100,45,25,40,'Common','/img/shellder.png'),(91,'Cloyster','Water','Ice',525,50,95,180,85,45,70,'Epic','/img/cloyster.png'),(92,'Gastly','Ghost','Poison',310,30,35,30,100,35,80,'Uncommon','/img/gastly.png'),(93,'Haunter','Ghost','Poison',405,45,50,45,115,55,95,'Rare','/img/haunter.png'),(94,'Gengar','Ghost','Poison',500,60,65,60,130,75,110,'Epic','/img/gengar.png'),(95,'Onix','Rock','Ground',385,35,45,160,30,45,70,'Uncommon','/img/onix.png'),(96,'Drowzee','Psychic','',328,60,48,45,43,90,42,'Common','/img/drowzee.png'),(97,'Hypno','Psychic','',483,85,73,70,73,115,67,'Rare','/img/hypno.png'),(98,'Krabby','Water','',325,30,105,90,25,25,50,'Common','/img/krabby.png'),(99,'Kingler','Water','',475,55,130,115,50,50,75,'Uncommon','/img/kingler.png'),(100,'Voltorb','Electric','',330,40,30,50,55,55,100,'Common','/img/voltorb.png'),(101,'Electrode','Electric','',480,60,50,70,80,80,140,'Rare','/img/electrode.png'),(102,'Exeggcute','Grass','Psychic',325,60,40,80,60,45,40,'Common','/img/exeggcute.png'),(103,'Exeggutor','Grass','Psychic',520,95,95,85,125,65,55,'Epic','/img/exeggutor.png'),(104,'Cubone','Ground','',320,50,50,95,40,50,35,'Common','/img/cubone.png'),(105,'Marowak','Ground','',425,60,80,110,50,80,45,'Uncommon','/img/marowak.png'),(106,'Hitmonlee','Fighting','',455,50,120,53,35,110,87,'Rare','/img/hitmonlee.png'),(107,'Hitmonchan','Fighting','',455,50,105,79,35,110,76,'Rare','/img/hitmonchan.png'),(108,'Lickitung','Normal','',385,90,55,75,60,75,30,'Uncommon','/img/lickitung.png'),(109,'Koffing','Poison','',340,40,65,95,60,45,35,'Common','/img/koffing.png'),(110,'Weezing','Poison','',490,65,90,120,85,70,60,'Rare','/img/weezing.png'),(111,'Rhyhorn','Ground','Rock',345,80,85,95,30,30,25,'Uncommon','/img/rhyhorn.png'),(112,'Rhydon','Ground','Rock',485,105,130,120,45,45,40,'Rare','/img/rhydon.png'),(113,'Chansey','Normal','',450,250,5,5,35,105,50,'Rare','/img/chansey.png'),(114,'Tangela','Grass','',435,65,55,115,100,40,60,'Uncommon','/img/tangela.png'),(115,'Kangaskhan','Normal','',490,105,95,80,40,80,90,'Rare','/img/kangaskhan.png'),(116,'Horsea','Water','',295,30,40,70,70,25,60,'Common','/img/horsea.png'),(117,'Seadra','Water','',440,55,65,95,95,45,85,'Uncommon','/img/seadra.png'),(118,'Goldeen','Water','',320,45,67,60,35,50,63,'Common','/img/goldeen.png'),(119,'Seaking','Water','',450,80,92,65,65,80,68,'Uncommon','/img/seaking.png'),(120,'Staryu','Water','',340,30,45,55,70,55,85,'Common','/img/staryu.png'),(121,'Starmie','Water','Psychic',520,60,75,85,100,85,115,'Epic','/img/starmie.png'),(122,'Mr. Mime','Psychic','Fairy',460,40,45,65,100,120,90,'Rare','/img/mr-mime.png'),(123,'Scyther','Bug','Flying',495,65,110,80,55,80,105,'Rare','/img/scyther.png'),(124,'Jynx','Ice','Psychic',455,65,50,35,115,95,95,'Rare','/img/jynx.png'),(125,'Electabuzz','Electric','',490,65,83,57,95,85,105,'Rare','/img/electabuzz.png'),(126,'Magmar','Fire','',495,65,95,57,100,85,93,'Rare','/img/magmar.png'),(127,'Pinsir','Bug','',500,65,125,100,55,70,85,'Rare','/img/pinsir.png'),(128,'Tauros','Normal','',490,75,100,95,40,70,110,'Rare','/img/tauros.png'),(129,'Magikarp','Water','',200,20,10,55,15,20,80,'Common','/img/magikarp.png'),(130,'Gyarados','Water','Flying',540,95,125,79,60,100,81,'Epic','/img/gyarados.png'),(131,'Lapras','Water','Ice',535,130,85,80,85,95,60,'Epic','/img/lapras.png'),(132,'Ditto','Normal','',288,48,48,48,48,48,48,'Rare','/img/ditto.png'),(133,'Eevee','Normal','',325,55,55,50,45,65,55,'Uncommon','/img/eevee.png'),(134,'Vaporeon','Water','',525,130,65,60,110,95,65,'Epic','/img/vaporeon.png'),(135,'Jolteon','Electric','',525,65,65,60,110,95,130,'Epic','/img/jolteon.png'),(136,'Flareon','Fire','',525,65,130,60,95,110,65,'Epic','/img/flareon.png'),(137,'Porygon','Normal','',395,65,60,70,85,75,40,'Uncommon','/img/porygon.png'),(138,'Omanyte','Rock','Water',355,35,40,100,90,55,35,'Uncommon','/img/omanyte.png'),(139,'Omastar','Rock','Water',495,70,60,125,115,70,55,'Rare','/img/omastar.png'),(140,'Kabuto','Rock','Water',355,30,80,90,55,45,55,'Uncommon','/img/kabuto.png'),(141,'Kabutops','Rock','Water',495,60,115,105,65,70,80,'Rare','/img/kabutops.png'),(142,'Aerodactyl','Rock','Flying',515,80,105,65,60,75,130,'Epic','/img/aerodactyl.png'),(143,'Snorlax','Normal','',540,160,110,65,65,110,30,'Epic','/img/snorlax.png'),(144,'Articuno','Ice','Flying',580,90,85,100,95,125,85,'Legendary','/img/articuno.png'),(145,'Zapdos','Electric','Flying',580,90,90,85,125,90,100,'Legendary','/img/zapdos.png'),(146,'Moltres','Fire','Flying',580,90,100,90,125,85,90,'Legendary','/img/moltres.png'),(147,'Dratini','Dragon','',300,41,64,45,50,50,50,'Rare','/img/dratini.png'),(148,'Dragonair','Dragon','',420,61,84,65,70,70,70,'Epic','/img/dragonair.png'),(149,'Dragonite','Dragon','Flying',600,91,134,95,100,100,80,'Legendary','/img/dragonite.png'),(150,'Mewtwo','Psychic','',680,106,110,90,154,90,130,'Legendary','/img/mewtwo.png'),(151,'Mew','Psychic','',600,100,100,100,100,100,100,'Legendary','/img/mew.png');
/*!40000 ALTER TABLE `gacha` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transaction`
--

DROP TABLE IF EXISTS `transaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transaction` (
  `TransactionId` int NOT NULL AUTO_INCREMENT,
  `UserOwner` int DEFAULT NULL,
  `GachaId` int NOT NULL,
  `RequestingUser` int DEFAULT NULL,
  `StartingPrice` int NOT NULL,
  `ActualPrice` int NOT NULL,
  `EndDate` varchar(45) DEFAULT NULL,
  `SendedTo` int DEFAULT NULL,
  PRIMARY KEY (`TransactionId`),
  UNIQUE KEY `TransactionId_UNIQUE` (`TransactionId`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transaction`
--

LOCK TABLES `transaction` WRITE;
/*!40000 ALTER TABLE `transaction` DISABLE KEYS */;
INSERT INTO `transaction` VALUES (4,NULL,1,51,10,21,'2024-12-02 03:03:26',6),(5,NULL,1,1,10,0,'2024-11-18 17:11:56',NULL),(6,NULL,1,1,10,0,'2024-11-18 17:11:56',NULL),(7,51,1,51,20,22,'2024-12-29 00:41:35',NULL);
/*!40000 ALTER TABLE `transaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `UserId` int NOT NULL AUTO_INCREMENT,
  `FirstName` varchar(45) NOT NULL,
  `LastName` varchar(45) NOT NULL,
  `Email` varchar(45) NOT NULL,
  `Password` varchar(45) NOT NULL,
  `CurrencyAmount` int DEFAULT NULL,
  PRIMARY KEY (`UserId`),
  UNIQUE KEY `Email_UNIQUE` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'Taylor','Smith','taylor.smith@example.com','b259fe071c41a754',200),(2,'Jane','Smith','jane.smith@domain.com','856ed03589098fa2',379),(3,'Taylor','Johnson','taylor.johnson@example.com','f6623cdcf7261c4c',484),(4,'Alex','Rodriguez','alex.rodriguez@example.com','c81114ee6d217c69',188),(5,'John','Miller','john.miller@example.com','9d7a0edd91e66aa4',327),(6,'Jamie','Smith','jamie.smith@domain.com','1b131ad0cfc411b3',864),(7,'Jane','Doe','jane.doe@example.com','3e74ca2642a01ff0',813),(8,'Alex','Miller','alex.miller@domain.com','abc92e6592d68854',949),(9,'Sam','Williams','sam.williams@example.com','f615551ca564bd8d',146),(10,'Sam','Smith','sam.smith@domain.com','db60eedf2c5ea577',592),(11,'John','Garcia','john.garcia@domain.com','b9a851aad2817a56',907),(12,'Chris','Garcia','chris.garcia@example.com','ce57d76f483c11af',161),(13,'Pat','Doe','pat.doe@example.com','6665817a7b633348',118),(14,'Alex','Johnson','alex.johnson@example.com','6d6653c9138f670d',668),(15,'Jamie','Jones','jamie.jones@domain.com','d27be2cd210db40d',922),(16,'Chris','Doe','chris.doe@domain.com','2aba4463292069da',416),(17,'Jane','Miller','jane.miller@mail.com','93074e82883f570d',375),(18,'Jane','Brown','jane.brown@example.com','79f2b93f9ff99f27',21),(19,'Chris','Rodriguez','chris.rodriguez@mail.com','8ff34199fd727cb4',264),(20,'Alex','Garcia','alex.garcia@mail.com','edec989bf6724817',742),(21,'Alex','Smith','alex.smith@mail.com','3a95dd08fe694365',2),(22,'Sam','Rodriguez','sam.rodriguez@example.com','a5a0ae793ddef2d4',351),(23,'Jamie','Doe','jamie.doe@mail.com','19eaf6a41376f15a',687),(24,'Pat','Williams','pat.williams@mail.com','94f647e2b714eeb1',239),(25,'Chris','Brown','chris.brown@example.com','d9e90e631a9c2116',38),(26,'Jordan','Williams','jordan.williams@domain.com','9309f6e2c5a33d89',148),(27,'Jamie','Johnson','jamie.johnson@mail.com','9ac4ba37dc4f8b3c',281),(28,'Sam','Garcia','sam.garcia@domain.com','cbf4b81baba0ddf3',190),(29,'Sam','Miller','sam.miller@mail.com','77eb70823166cb15',743),(30,'Sam','Johnson','sam.johnson@mail.com','1b7940170a80859e',109),(31,'Kim','Miller','kim.miller@example.com','f5053b08bf2a094b',608),(32,'Jane','Johnson','jane.johnson@mail.com','2e4074bc8b30d18e',161),(33,'Pat','Smith','pat.smith@mail.com','ce08353308a16481',35),(34,'Pat','Davis','pat.davis@mail.com','ba4f459974a0ab41',677),(35,'Taylor','Smith','taylor.smith@domain.com','56e0922b0f081bcd',891),(36,'Jane','Doe','jane.doe@domain.com','1e790adfcff04c1e',949),(37,'Jordan','Garcia','jordan.garcia@mail.com','851baf1054e06c6f',536),(40,'Taylor','Williams','taylor.williams@mail.com','85952420f1619ea0',239),(41,'Alex','Jones','alex.jones@domain.com','065b8854cec78a65',39),(42,'Jane','Garcia','jane.garcia@example.com','4c6dce1bfa4e23f7',791),(43,'Chris','Rodriguez','chris.rodriguez@domain.com','b5d052d57299f5aa',932),(44,'John','Rodriguez','john.rodriguez@example.com','7eac9ced515f333d',31),(45,'Pat','Johnson','pat.johnson@mail.com','7e05cef18450c010',547),(46,'Jamie','Brown','jamie.brown@domain.com','07f0332ed6d9b895',94),(47,'Sam','Doe','sam.doe@domain.com','dceec3693577db9e',181),(48,'Alex','Brown','a','a1ea6f198f4a7510',49),(50,'Jane','Davis','jane.davis@domain.com','d3a685a273ac4284',180),(51,'Aldo','Baglio','aldo.baglio@example.com','ciao',78);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-02 21:17:08
