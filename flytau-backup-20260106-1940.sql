-- MySQL dump 10.13  Distrib 9.5.0, for macos15.7 (arm64)
--
-- Host: localhost    Database: flytau
-- ------------------------------------------------------
-- Server version	9.5.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '8a2cba52-eaf5-11f0-963f-5ae778a1bfda:1-172';

--
-- Table structure for table `Airplanes`
--

DROP TABLE IF EXISTS `Airplanes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Airplanes` (
  `AirplaneId` varchar(45) NOT NULL,
  `PurchaseDate` date DEFAULT NULL,
  `Manufacturer` varchar(45) DEFAULT NULL,
  `Couch (Rows, Cols)` varchar(45) DEFAULT NULL,
  `Business (Rows, Cols)` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`AirplaneId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Airplanes`
--

LOCK TABLES `Airplanes` WRITE;
/*!40000 ALTER TABLE `Airplanes` DISABLE KEYS */;
INSERT INTO `Airplanes` VALUES ('A001','2015-06-01','Boeing','20 6','5 4'),('A002','2016-07-15','Boeing','20 6','5 4'),('A003','2018-09-10','Airbus','25 6','6 4'),('A005','2014-11-30','Dassault','10 4',NULL),('PLANE-001','2020-01-15','Boeing','20 6','5 4'),('PLANE-002','2021-06-10','Boeing','20 6','5 4'),('PLANE-004','2019-11-20','Airbus','22 6','5 4'),('PLANE-005','2023-01-01','Dassault','10 4',NULL);
/*!40000 ALTER TABLE `Airplanes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FlightAttendant`
--

DROP TABLE IF EXISTS `FlightAttendant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FlightAttendant` (
  `Id` varchar(45) NOT NULL,
  `PhoneNum` json DEFAULT NULL,
  `FirstName` varchar(45) DEFAULT NULL,
  `SecondName` varchar(45) DEFAULT NULL,
  `JoinDate` date DEFAULT NULL,
  `Street` varchar(45) DEFAULT NULL,
  `City` varchar(45) DEFAULT NULL,
  `HouseNum` varchar(45) DEFAULT NULL,
  `LongFlightsTraining` tinyint DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FlightAttendant`
--

LOCK TABLES `FlightAttendant` WRITE;
/*!40000 ALTER TABLE `FlightAttendant` DISABLE KEYS */;
INSERT INTO `FlightAttendant` VALUES ('A001','[\"972-50-1111111\"]','Maya','Stern','2017-03-01','Cabin Rd','Tel Aviv','2',1),('A002','[\"972-52-1212121\"]','Noa','Klein','2018-04-10','Cabin Rd','Tel Aviv','4',1),('A003','[\"972-54-1313131\"]','Shira','Wolf','2017-05-12','Service St','Haifa','6',1),('A004','[\"972-50-1414141\"]','Yael','Berger','2019-01-20','Service St','Haifa','8',1),('A005','[\"972-52-1515151\"]','Tamar','Fischer','2019-06-05','Cabin Ave','Netanya','3',1),('A006','[\"972-54-1616161\"]','Liora','Schwartz','2016-07-07','Cabin Ave','Netanya','5',1),('A007','[\"972-50-1717171\"]','Dana','Weiss','2018-10-10','Crew St','Beersheba','11',1),('A008','[\"972-52-1818181\"]','Ronit','Newman','2020-02-02','Crew St','Beersheba','13',1),('A009','[\"972-54-1919191\"]','Michal','Gross','2017-08-08','Flight Rd','Raman','7',1),('A010','[\"972-50-2020202\"]','Efrat','Blum','2018-11-11','Flight Rd','Raman','9',1),('A011','[\"972-52-2121212\"]','Hila','Marcus','2016-12-12','Service Ln','Hebron','2',1),('A012','[\"972-54-2222223\"]','Keren','Simon','2019-03-03','Service Ln','Hebron','4',1),('A013','[\"972-50-2323232\"]','Inbar','Green','2021-01-01','Cabin Ct','Ramla','1',0),('A014','[\"972-52-2424242\"]','Amit','Silver','2021-05-05','Cabin Ct','Ramla','3',0),('A015','[\"972-54-2525252\"]','Sivan','Bloom','2022-02-02','Crew Blvd','Afula','6',0),('A016','[\"972-50-2626262\"]','Rotem','Fine','2020-09-09','Crew Blvd','Afula','8',0),('A017','[\"972-52-2727272\"]','Gili','Hart','2019-07-07','Cabin Way','Kfar Saba','12',0),('A018','[\"972-54-2828282\"]','Lior','Stone','2018-06-06','Cabin Way','Kfar Saba','14',0),('A019','[\"972-50-2929292\"]','Adi','Glass','2020-10-10','Flight Ave','Eilat','9',0),('A020','[\"972-52-3030303\"]','Chen','Gold','2019-09-09','Flight Ave','Eilat','11',0),('ATT-1','[\"0504000001\"]','Maya','Dagan','2020-01-01','Arlozorov','Tel Aviv','40',1),('ATT-2','[\"0504000002\"]','Adi','Ziv','2021-01-01','Sokolov','Herzliya','18',0);
/*!40000 ALTER TABLE `FlightAttendant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FlightAttendant_has_Flights`
--

DROP TABLE IF EXISTS `FlightAttendant_has_Flights`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FlightAttendant_has_Flights` (
  `FlightAttendant_Id` varchar(45) NOT NULL,
  `Flights_FlightId` varchar(45) NOT NULL,
  `Flights_Airplanes_AirplaneId` varchar(45) NOT NULL,
  PRIMARY KEY (`FlightAttendant_Id`,`Flights_FlightId`,`Flights_Airplanes_AirplaneId`),
  KEY `fk_FlightAttendant_has_Flights_Flights1_idx` (`Flights_FlightId`,`Flights_Airplanes_AirplaneId`),
  KEY `fk_FlightAttendant_has_Flights_FlightAttendant1_idx` (`FlightAttendant_Id`),
  CONSTRAINT `fk_FlightAttendant_has_Flights_FlightAttendant1` FOREIGN KEY (`FlightAttendant_Id`) REFERENCES `FlightAttendant` (`Id`),
  CONSTRAINT `fk_FlightAttendant_has_Flights_Flights1` FOREIGN KEY (`Flights_FlightId`, `Flights_Airplanes_AirplaneId`) REFERENCES `Flights` (`FlightId`, `Airplanes_AirplaneId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FlightAttendant_has_Flights`
--

LOCK TABLES `FlightAttendant_has_Flights` WRITE;
/*!40000 ALTER TABLE `FlightAttendant_has_Flights` DISABLE KEYS */;
INSERT INTO `FlightAttendant_has_Flights` VALUES ('A001','FT101','A001'),('A002','FT101','A001'),('A003','FT101','A001'),('A004','FT101','A001'),('A005','FT101','A001'),('A006','FT101','A001'),('A007','FT102','A003'),('A008','FT102','A003'),('A009','FT102','A003'),('A010','FT102','A003'),('A013','FT103','A005'),('A014','FT103','A005'),('A015','FT103','A005'),('A016','FT104','A002'),('A017','FT104','A002'),('A018','FT104','A002'),('A019','FT104','A002'),('ATT-1','FL-101','PLANE-001'),('ATT-2','FL-102','PLANE-002');
/*!40000 ALTER TABLE `FlightAttendant_has_Flights` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Flights`
--

DROP TABLE IF EXISTS `Flights`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Flights` (
  `FlightId` varchar(45) NOT NULL,
  `Status` varchar(45) DEFAULT NULL,
  `EconomyPrice` decimal(10,2) DEFAULT NULL,
  `BusinessPrice` decimal(10,2) DEFAULT NULL,
  `Duration` int DEFAULT NULL COMMENT 'Duration in minutes',
  `DepartureDate` date DEFAULT NULL,
  `DepartureHour` varchar(45) DEFAULT NULL,
  `OriginPort` varchar(45) NOT NULL,
  `DestPort` varchar(45) NOT NULL,
  `Airplanes_AirplaneId` varchar(45) NOT NULL,
  PRIMARY KEY (`FlightId`,`Airplanes_AirplaneId`),
  KEY `fk_Flights_Airplanes1_idx` (`Airplanes_AirplaneId`),
  CONSTRAINT `fk_Flights_Airplanes1` FOREIGN KEY (`Airplanes_AirplaneId`) REFERENCES `Airplanes` (`AirplaneId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Flights`
--

LOCK TABLES `Flights` WRITE;
/*!40000 ALTER TABLE `Flights` DISABLE KEYS */;
INSERT INTO `Flights` VALUES ('FL-101','Completed',800.00,1500.00,720,'2025-12-10','10:00','TLV','JFK','PLANE-001'),('FL-102','Completed',150.00,NULL,60,'2025-12-12','08:00','TLV','LCA','PLANE-002'),('FL-103','Active',450.00,950.00,300,'2026-01-20','12:00','TLV','LHR','PLANE-004'),('FL-104','Cancelled',700.00,1200.00,660,'2026-01-25','22:00','TLV','BKK','PLANE-005'),('FT101','active',500.00,1500.00,660,'2025-02-15','08:00:00','Tel Aviv','New York','A001'),('FT102','active',300.00,900.00,300,'2025-02-16','10:00:00','Tel Aviv','London','A003'),('FT103','active',250.00,NULL,270,'2025-02-17','14:00:00','Tel Aviv','Paris','A005'),('FT104','active',150.00,450.00,120,'2025-02-18','06:00:00','Tel Aviv','Athens','A002');
/*!40000 ALTER TABLE `Flights` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `GuestCustomer`
--

DROP TABLE IF EXISTS `GuestCustomer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `GuestCustomer` (
  `UniqueMail` varchar(45) NOT NULL,
  `PhoneNum` json DEFAULT NULL,
  `FirstName` varchar(45) DEFAULT NULL,
  `SecondName` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`UniqueMail`),
  UNIQUE KEY `UniqueMail_UNIQUE` (`UniqueMail`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `GuestCustomer`
--

LOCK TABLES `GuestCustomer` WRITE;
/*!40000 ALTER TABLE `GuestCustomer` DISABLE KEYS */;
INSERT INTO `GuestCustomer` VALUES ('guest1@example.com','[\"972-50-0000000\"]','Guest','User'),('guest1@gmail.com','[\"0541112223\"]','Guest','Account');
/*!40000 ALTER TABLE `GuestCustomer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Managers`
--

DROP TABLE IF EXISTS `Managers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Managers` (
  `ManagerId` varchar(45) NOT NULL,
  `PhoneNum` json DEFAULT NULL,
  `FirstName` varchar(45) DEFAULT NULL,
  `SecondName` varchar(45) DEFAULT NULL,
  `JoinDate` date DEFAULT NULL,
  `Street` varchar(45) DEFAULT NULL,
  `City` varchar(45) DEFAULT NULL,
  `HouseNum` varchar(45) DEFAULT NULL,
  `Password` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ManagerId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Managers`
--

LOCK TABLES `Managers` WRITE;
/*!40000 ALTER TABLE `Managers` DISABLE KEYS */;
INSERT INTO `Managers` VALUES ('M001','[\"972-54-1234567\"]','David','Cohen','2018-05-01','Main St','Tel Aviv','10','$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6'),('M002','[\"972-50-7654321\"]','Sarah','Levi','2019-09-15','Derech Ben Gurion','Jerusalem','20','$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6'),('MGR-1','[\"0501111111\"]','Avraham','Levi','2020-01-01','Herzl','Tel Aviv','10','admin123'),('MGR-2','[\"0502222222\"]','Sarah','Cohen','2020-05-15','Rothschild','Tel Aviv','22','admin456');
/*!40000 ALTER TABLE `Managers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Managers_edits_Flights`
--

DROP TABLE IF EXISTS `Managers_edits_Flights`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Managers_edits_Flights` (
  `Managers_ManagerId` varchar(45) NOT NULL,
  `Flights_FlightId` varchar(45) NOT NULL,
  `Flights_Airplanes_AirplaneId` varchar(45) NOT NULL,
  PRIMARY KEY (`Managers_ManagerId`,`Flights_FlightId`,`Flights_Airplanes_AirplaneId`),
  KEY `fk_Managers_has_Flights_Flights1_idx` (`Flights_FlightId`,`Flights_Airplanes_AirplaneId`),
  KEY `fk_Managers_has_Flights_Managers1_idx` (`Managers_ManagerId`),
  CONSTRAINT `fk_Managers_has_Flights_Flights1` FOREIGN KEY (`Flights_FlightId`, `Flights_Airplanes_AirplaneId`) REFERENCES `Flights` (`FlightId`, `Airplanes_AirplaneId`),
  CONSTRAINT `fk_Managers_has_Flights_Managers1` FOREIGN KEY (`Managers_ManagerId`) REFERENCES `Managers` (`ManagerId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Managers_edits_Flights`
--

LOCK TABLES `Managers_edits_Flights` WRITE;
/*!40000 ALTER TABLE `Managers_edits_Flights` DISABLE KEYS */;
INSERT INTO `Managers_edits_Flights` VALUES ('M001','FT101','A001'),('M001','FT102','A003'),('M002','FT103','A005'),('M002','FT104','A002');
/*!40000 ALTER TABLE `Managers_edits_Flights` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `UniqueOrderCode` varchar(45) NOT NULL,
  `TotalCost` decimal(10,2) DEFAULT NULL,
  `Class` varchar(45) DEFAULT NULL,
  `Status` varchar(45) DEFAULT NULL,
  `GuestCustomer_UniqueMail` varchar(45) DEFAULT NULL,
  `RegisteredCustomer_UniqueMail` varchar(45) DEFAULT NULL,
  `Flights_FlightId` varchar(45) NOT NULL,
  `Flights_Airplanes_AirplaneId` varchar(45) NOT NULL,
  `CreatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`UniqueOrderCode`),
  KEY `fk_orders_GuestCustomer_idx` (`GuestCustomer_UniqueMail`),
  KEY `fk_orders_RegisteredCustomer1_idx` (`RegisteredCustomer_UniqueMail`),
  KEY `fk_orders_Flights1_idx` (`Flights_FlightId`,`Flights_Airplanes_AirplaneId`),
  CONSTRAINT `fk_orders_Flights1` FOREIGN KEY (`Flights_FlightId`, `Flights_Airplanes_AirplaneId`) REFERENCES `Flights` (`FlightId`, `Airplanes_AirplaneId`),
  CONSTRAINT `fk_orders_GuestCustomer` FOREIGN KEY (`GuestCustomer_UniqueMail`) REFERENCES `GuestCustomer` (`UniqueMail`),
  CONSTRAINT `fk_orders_RegisteredCustomer1` FOREIGN KEY (`RegisteredCustomer_UniqueMail`) REFERENCES `RegisteredCustomer` (`UniqueMail`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES ('FLY-ABC123',1000.00,'economy','confirmed',NULL,'customer1@example.com','FT101','A001','2026-01-06 15:06:01'),('FLY-DEF456',900.00,'business','confirmed',NULL,'customer2@example.com','FT102','A003','2026-01-06 15:06:01'),('ORD-001',1600.00,'Economy','Completed',NULL,'user1@example.com','FL-101','PLANE-001','2026-01-06 17:00:45'),('ORD-002',7.50,'Economy','Cancelled_Customer','guest1@gmail.com',NULL,'FL-102','PLANE-002','2026-01-06 17:00:45'),('ORD-003',0.00,'Business','Cancelled_System',NULL,'user2@example.com','FL-104','PLANE-005','2026-01-06 17:00:45');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Pilot`
--

DROP TABLE IF EXISTS `Pilot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Pilot` (
  `Id` varchar(45) NOT NULL,
  `PhoneNum` json DEFAULT NULL,
  `FirstName` varchar(45) DEFAULT NULL,
  `SecondName` varchar(45) DEFAULT NULL,
  `JoinDate` date DEFAULT NULL,
  `Street` varchar(45) DEFAULT NULL,
  `City` varchar(45) DEFAULT NULL,
  `HouseNum` varchar(45) DEFAULT NULL,
  `LongFlightsTraining` tinyint DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Pilot`
--

LOCK TABLES `Pilot` WRITE;
/*!40000 ALTER TABLE `Pilot` DISABLE KEYS */;
INSERT INTO `Pilot` VALUES ('P001','[\"972-52-1111111\"]','Yossi','Mizrahi','2016-02-01','Pilot Ave','Tel Aviv','12',1),('P002','[\"972-54-2222222\"]','Avi','Goldberg','2016-03-10','Pilot Ave','Tel Aviv','14',1),('P003','[\"972-50-3333333\"]','Moshe','Peretz','2017-05-20','Aviation Rd','Tel Aviv','16',1),('P004','[\"972-52-4444444\"]','Dan','Shapiro','2018-01-15','Aviation Rd','Tel Aviv','18',1),('P005','[\"972-54-5555555\"]','Eitan','Rosen','2019-06-30','Pilot St','Haifa','4',1),('P006','[\"972-50-6666666\"]','Uri','Katz','2015-12-01','Pilot St','Haifa','6',1),('P007','[\"972-52-7777777\"]','Noam','Ben-David','2020-07-01','Crew Ln','Netanya','3',0),('P008','[\"972-54-8888888\"]','Gal','Friedman','2021-04-12','Crew Ln','Netanya','5',0),('P009','[\"972-50-9999999\"]','Oren','Levy','2019-09-09','Air St','Ramat Gan','8',0),('P010','[\"972-52-1010101\"]','Tal','Avraham','2020-11-11','Air St','Ramat Gan','10',0),('PLT-1','[\"0503000001\"]','Itay','Barak','2018-01-01','Bograshov','Tel Aviv','5',1),('PLT-2','[\"0503000002\"]','Noam','Shamir','2018-01-01','Hahagana','Haifa','12',1),('PLT-3','[\"0503000003\"]','Guy','Erez','2019-06-01','Yefet','Jaffa','3',0);
/*!40000 ALTER TABLE `Pilot` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Pilot_has_Flights`
--

DROP TABLE IF EXISTS `Pilot_has_Flights`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Pilot_has_Flights` (
  `Pilot_Id` varchar(45) NOT NULL,
  `Flights_FlightId` varchar(45) NOT NULL,
  `Flights_Airplanes_AirplaneId` varchar(45) NOT NULL,
  PRIMARY KEY (`Pilot_Id`,`Flights_FlightId`,`Flights_Airplanes_AirplaneId`),
  KEY `fk_Pilot_has_Flights_Flights1_idx` (`Flights_FlightId`,`Flights_Airplanes_AirplaneId`),
  KEY `fk_Pilot_has_Flights_Pilot1_idx` (`Pilot_Id`),
  CONSTRAINT `fk_Pilot_has_Flights_Flights1` FOREIGN KEY (`Flights_FlightId`, `Flights_Airplanes_AirplaneId`) REFERENCES `Flights` (`FlightId`, `Airplanes_AirplaneId`),
  CONSTRAINT `fk_Pilot_has_Flights_Pilot1` FOREIGN KEY (`Pilot_Id`) REFERENCES `Pilot` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Pilot_has_Flights`
--

LOCK TABLES `Pilot_has_Flights` WRITE;
/*!40000 ALTER TABLE `Pilot_has_Flights` DISABLE KEYS */;
INSERT INTO `Pilot_has_Flights` VALUES ('P001','FT101','A001'),('P002','FT101','A001'),('P003','FT101','A001'),('P004','FT102','A003'),('P005','FT102','A003'),('P007','FT103','A005'),('P008','FT103','A005'),('P009','FT104','A002'),('P010','FT104','A002'),('PLT-1','FL-101','PLANE-001'),('PLT-2','FL-101','PLANE-001'),('PLT-3','FL-102','PLANE-002');
/*!40000 ALTER TABLE `Pilot_has_Flights` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RegisteredCustomer`
--

DROP TABLE IF EXISTS `RegisteredCustomer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RegisteredCustomer` (
  `UniqueMail` varchar(45) NOT NULL,
  `PhoneNum` json DEFAULT NULL,
  `FirstName` varchar(45) DEFAULT NULL,
  `SecondName` varchar(45) DEFAULT NULL,
  `Password` varchar(255) NOT NULL,
  `RegistrationDate` date DEFAULT NULL,
  `PassportNum` varchar(45) DEFAULT NULL,
  `BirthDate` date DEFAULT NULL,
  PRIMARY KEY (`UniqueMail`),
  UNIQUE KEY `UniqueMail_UNIQUE` (`UniqueMail`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RegisteredCustomer`
--

LOCK TABLES `RegisteredCustomer` WRITE;
/*!40000 ALTER TABLE `RegisteredCustomer` DISABLE KEYS */;
INSERT INTO `RegisteredCustomer` VALUES ('customer1@example.com','[\"972-54-1111111\"]','John','Doe','$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6','2020-01-01','P123456','1985-06-15'),('customer2@example.com','[\"972-54-2222222\"]','Jane','Smith','$2b$12$iprkA2Ulb3EIipYD.lErfOrsM4L4rR.tME9Uqiy6zTpVszd3dOTN6','2021-02-15','P789012','1990-09-22'),('user1@example.com','[\"0525555555\"]','John','Doe','pass1','2025-01-01','12345678','1990-05-15'),('user2@example.com','[\"0526666666\"]','Jane','Smith','pass2','2025-02-10','87654321','1985-11-20');
/*!40000 ALTER TABLE `RegisteredCustomer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Tickets`
--

DROP TABLE IF EXISTS `Tickets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Tickets` (
  `TicketId` int NOT NULL AUTO_INCREMENT,
  `Class` varchar(45) DEFAULT NULL,
  `RowNum` int NOT NULL,
  `Seat` varchar(45) NOT NULL,
  `Price` decimal(10,2) DEFAULT NULL,
  `orders_UniqueOrderCode` varchar(45) NOT NULL,
  `Flights_FlightId` varchar(45) NOT NULL,
  `Flights_Airplanes_AirplaneId` varchar(45) NOT NULL,
  PRIMARY KEY (`TicketId`),
  UNIQUE KEY `unique_seat_per_flight` (`Flights_FlightId`,`Flights_Airplanes_AirplaneId`,`RowNum`,`Seat`),
  KEY `fk_Tickets_orders1_idx` (`orders_UniqueOrderCode`),
  KEY `fk_Tickets_Flights1_idx` (`Flights_FlightId`,`Flights_Airplanes_AirplaneId`),
  CONSTRAINT `fk_Tickets_Flights1` FOREIGN KEY (`Flights_FlightId`, `Flights_Airplanes_AirplaneId`) REFERENCES `Flights` (`FlightId`, `Airplanes_AirplaneId`),
  CONSTRAINT `fk_Tickets_orders1` FOREIGN KEY (`orders_UniqueOrderCode`) REFERENCES `orders` (`UniqueOrderCode`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Tickets`
--

LOCK TABLES `Tickets` WRITE;
/*!40000 ALTER TABLE `Tickets` DISABLE KEYS */;
INSERT INTO `Tickets` VALUES (1,'economy',6,'A',500.00,'FLY-ABC123','FT101','A001'),(2,'economy',6,'B',500.00,'FLY-ABC123','FT101','A001'),(3,'business',1,'A',900.00,'FLY-DEF456','FT102','A003'),(13,'Economy',10,'A',800.00,'ORD-001','FL-101','PLANE-001'),(14,'Economy',10,'B',800.00,'ORD-001','FL-101','PLANE-001'),(15,'Economy',5,'C',150.00,'ORD-002','FL-102','PLANE-002');
/*!40000 ALTER TABLE `Tickets` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-06 19:40:20
