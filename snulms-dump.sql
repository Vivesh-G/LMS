-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: snulms
-- ------------------------------------------------------
-- Server version	5.5.5-10.4.32-MariaDB

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
  `ID` int(11) NOT NULL,
  `AdminID` int(11) NOT NULL AUTO_INCREMENT,
  `LastAccess` datetime DEFAULT NULL,
  PRIMARY KEY (`AdminID`),
  KEY `ID` (`ID`),
  CONSTRAINT `admin_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `users` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (0,1,NULL);
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance` (
  `AttendanceID` int(11) NOT NULL AUTO_INCREMENT,
  `StudentID` int(11) NOT NULL,
  `CourseID` varchar(20) NOT NULL,
  `Date` date NOT NULL,
  `Attendance` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`AttendanceID`),
  KEY `StudentID` (`StudentID`),
  KEY `CourseID` (`CourseID`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`StudentID`) REFERENCES `student` (`ID`),
  CONSTRAINT `attendance_ibfk_2` FOREIGN KEY (`CourseID`) REFERENCES `courses` (`CourseID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance`
--

LOCK TABLES `attendance` WRITE;
/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
INSERT INTO `attendance` VALUES (1,3,'CS2001T','2025-03-18',1),(2,3,'CS2004','2025-03-19',1),(3,4,'CS2004','2025-03-19',0),(4,3,'CS2001T','2025-03-25',1),(5,3,'CS2004','2025-03-26',0),(6,4,'CS2004','2025-03-26',1);
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coursecontent`
--

DROP TABLE IF EXISTS `coursecontent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `coursecontent` (
  `CourseContentID` int(11) NOT NULL AUTO_INCREMENT,
  `CCName` varchar(200) NOT NULL,
  `Description` mediumtext DEFAULT NULL,
  `FileUrl` text DEFAULT NULL,
  `UploadDate` date NOT NULL,
  `IsAssignment` tinyint(1) DEFAULT NULL,
  `CourseID` varchar(20) NOT NULL,
  `UploadedBy` int(11) NOT NULL,
  `DueDate` datetime DEFAULT NULL,
  `TotalMarks` int(11) DEFAULT NULL,
  PRIMARY KEY (`CourseContentID`),
  KEY `UploadedBy` (`UploadedBy`),
  KEY `CourseID` (`CourseID`),
  CONSTRAINT `coursecontent_ibfk_1` FOREIGN KEY (`UploadedBy`) REFERENCES `faculty` (`FacultyID`),
  CONSTRAINT `coursecontent_ibfk_2` FOREIGN KEY (`CourseID`) REFERENCES `courses` (`CourseID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coursecontent`
--

LOCK TABLES `coursecontent` WRITE;
/*!40000 ALTER TABLE `coursecontent` DISABLE KEYS */;
INSERT INTO `coursecontent` VALUES (1,'UNIT 1','STUDY ON YOUR OWN!','Nil','2025-03-01',0,'CS2004',2,NULL,NULL),(2,'UNIT 2','MIDSEM PORTION','NIL','2025-03-01',0,'CS2004',2,NULL,NULL),(3,'UNIT 1','ER DIAGRAMS','NIL','2025-03-01',0,'CS2001T',1,NULL,NULL);
/*!40000 ALTER TABLE `coursecontent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `courses` (
  `CourseID` varchar(20) NOT NULL,
  `CourseName` varchar(100) NOT NULL,
  `CourseCredit` int(11) NOT NULL,
  `Category` varchar(50) DEFAULT NULL,
  `SemesterNo` int(11) NOT NULL,
  `FacultyID` int(11) NOT NULL,
  `DepartmentID` int(11) NOT NULL,
  PRIMARY KEY (`CourseID`),
  UNIQUE KEY `CourseID` (`CourseID`),
  KEY `DepartmentID` (`DepartmentID`),
  KEY `FacultyID` (`FacultyID`),
  CONSTRAINT `courses_ibfk_1` FOREIGN KEY (`DepartmentID`) REFERENCES `department` (`DepartmentID`),
  CONSTRAINT `courses_ibfk_2` FOREIGN KEY (`FacultyID`) REFERENCES `faculty` (`FacultyID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

LOCK TABLES `courses` WRITE;
/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
INSERT INTO `courses` VALUES ('CS2001T','DataBase Management Systems',3,'Core',4,1,1),('CS2004','Design and Analysis of Algorithms',3,'Core',4,2,1);
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `DepartmentID` int(11) NOT NULL AUTO_INCREMENT,
  `DepartmentName` varchar(100) NOT NULL,
  `HODName` varchar(100) NOT NULL,
  `UniversityID` int(11) DEFAULT NULL,
  PRIMARY KEY (`DepartmentID`),
  KEY `UniversityID` (`UniversityID`),
  CONSTRAINT `department_ibfk_1` FOREIGN KEY (`UniversityID`) REFERENCES `university` (`UniveristyID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department`
--

LOCK TABLES `department` WRITE;
/*!40000 ALTER TABLE `department` DISABLE KEYS */;
INSERT INTO `department` VALUES (1,'CSE','CSEHOD',0),(2,'COMMERCE','COMMERCEHOD',0);
/*!40000 ALTER TABLE `department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enrollment`
--

DROP TABLE IF EXISTS `enrollment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enrollment` (
  `EnrollmentID` int(11) NOT NULL AUTO_INCREMENT,
  `StudentID` int(11) NOT NULL,
  `CourseID` varchar(20) NOT NULL,
  `EnrollmentDate` date DEFAULT NULL,
  PRIMARY KEY (`EnrollmentID`),
  UNIQUE KEY `StudentID` (`StudentID`,`CourseID`),
  KEY `CourseID` (`CourseID`),
  CONSTRAINT `enrollment_ibfk_1` FOREIGN KEY (`StudentID`) REFERENCES `student` (`ID`),
  CONSTRAINT `enrollment_ibfk_2` FOREIGN KEY (`CourseID`) REFERENCES `courses` (`CourseID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enrollment`
--

LOCK TABLES `enrollment` WRITE;
/*!40000 ALTER TABLE `enrollment` DISABLE KEYS */;
INSERT INTO `enrollment` VALUES (1,3,'CS2001T','2025-03-15'),(2,3,'CS2004','2025-03-15'),(3,4,'CS2004','2025-03-16');
/*!40000 ALTER TABLE `enrollment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `faculty`
--

DROP TABLE IF EXISTS `faculty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faculty` (
  `ID` int(11) NOT NULL,
  `FacultyID` int(11) NOT NULL AUTO_INCREMENT,
  `PhoneNo` int(10) NOT NULL,
  `Qualification` varchar(200) NOT NULL,
  `Level` varchar(100) NOT NULL,
  `DepartmentID` int(11) NOT NULL,
  PRIMARY KEY (`FacultyID`),
  KEY `ID` (`ID`),
  KEY `DepartmentID` (`DepartmentID`),
  CONSTRAINT `faculty_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `users` (`ID`),
  CONSTRAINT `faculty_ibfk_2` FOREIGN KEY (`DepartmentID`) REFERENCES `department` (`DepartmentID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faculty`
--

LOCK TABLES `faculty` WRITE;
/*!40000 ALTER TABLE `faculty` DISABLE KEYS */;
INSERT INTO `faculty` VALUES (1,1,1234567890,'Ph.D(Computer Networks) ','Assistant Professor',1),(2,2,1234567890,'Ph.D. in Information and Communication Engineering','Professor',1);
/*!40000 ALTER TABLE `faculty` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `ID` int(11) NOT NULL,
  `RegistrationNo` int(11) NOT NULL AUTO_INCREMENT,
  `PhoneNo` int(10) NOT NULL,
  `Class` varchar(50) NOT NULL,
  `DoB` date NOT NULL,
  `Semester` varchar(50) NOT NULL,
  `DepartmentID` int(11) NOT NULL,
  PRIMARY KEY (`RegistrationNo`),
  KEY `ID` (`ID`),
  KEY `DepartmentID` (`DepartmentID`),
  CONSTRAINT `student_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `users` (`ID`),
  CONSTRAINT `student_ibfk_2` FOREIGN KEY (`DepartmentID`) REFERENCES `department` (`DepartmentID`)
) ENGINE=InnoDB AUTO_INCREMENT=2002 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` VALUES (3,157,1234567890,'AI & DS B','2005-12-12','4',1),(4,165,2147483647,'AI & DS B','2005-12-20','4',1);
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `submissions`
--

DROP TABLE IF EXISTS `submissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `submissions` (
  `SubmissionID` int(11) NOT NULL AUTO_INCREMENT,
  `StudentID` int(11) NOT NULL,
  `CCID` int(11) NOT NULL,
  `SubmissionDate` datetime DEFAULT NULL,
  `FileUrl` text DEFAULT NULL,
  `Grade` decimal(5,2) DEFAULT NULL,
  `Feedback` text DEFAULT NULL,
  PRIMARY KEY (`SubmissionID`),
  KEY `StudentID` (`StudentID`),
  KEY `CCID` (`CCID`),
  CONSTRAINT `submissions_ibfk_1` FOREIGN KEY (`StudentID`) REFERENCES `student` (`ID`),
  CONSTRAINT `submissions_ibfk_2` FOREIGN KEY (`CCID`) REFERENCES `coursecontent` (`CourseContentID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `submissions`
--

LOCK TABLES `submissions` WRITE;
/*!40000 ALTER TABLE `submissions` DISABLE KEYS */;
INSERT INTO `submissions` VALUES (1,3,1,'2025-03-20 14:30:00','uploads/student3_assignment1.pdf',85.50,'Good work, but needs more examples'),(2,4,1,'2025-03-21 10:15:00','uploads/student4_assignment1.pdf',92.00,'Excellent analysis'),(3,3,2,'2025-03-27 16:45:00','uploads/student3_assignment2.pdf',78.00,'Late submission, content is good');
/*!40000 ALTER TABLE `submissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `university`
--

DROP TABLE IF EXISTS `university`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `university` (
  `UniveristyID` int(11) NOT NULL,
  `UniversityName` varchar(100) NOT NULL,
  `Address` varchar(200) NOT NULL,
  `City` varchar(100) NOT NULL,
  `State` varchar(100) NOT NULL,
  `Pincode` int(6) NOT NULL,
  PRIMARY KEY (`UniveristyID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `university`
--

LOCK TABLES `university` WRITE;
/*!40000 ALTER TABLE `university` DISABLE KEYS */;
INSERT INTO `university` VALUES (0,'Shiv Nadar University Chennai','Kalvakkam','Chennai','Tamil Nadu',603105);
/*!40000 ALTER TABLE `university` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `ID` int(11) NOT NULL,
  `UserName` varchar(100) NOT NULL,
  `FirstName` varchar(100) NOT NULL,
  `LastName` varchar(100) DEFAULT NULL,
  `Role` enum('admin','faculty','student','') NOT NULL,
  `Email` varchar(50) DEFAULT NULL,
  `PasswordHash` varchar(500) NOT NULL,
  `CreatedOn` date NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (0,'admin','admin','','admin','admin@snulms.com','scrypt:32768:8:1$DCCnBWhqdyDSpYVL$1ad2514490dc829a185465200632b0fb9d20b54b20fe39d1b9dcd4db8108fb8f2d3fdbd37112fbb796880fb5c8ee74c43d9cc70cae0db5cd88c514971cc47441','2025-03-08'),(1,'Veeramani','Veeramani','S','faculty','veeramani@snulms.com','scrypt:32768:8:1$8na9olEKLCgdRcmu$0996dd26e77adc7ab04045982498e7c581de110411b77a2277e2c4dcd549b9cc6a5ca46190ce9f3a981cc500355f4e0874ae4f2eab104336ec370a8b14bd03ee','2025-03-08'),(2,'Milton','Milton','RS','faculty','rsmilton@snulms.com','scrypt:32768:8:1$Xqp3bNYc9dZmZHlu$577b8c06c670549e79c6766239f9f145ca4231386919568bca732bea853635667ed4b29638d66c5277bfcb19c7919dd05472af116e3407ddfc8aae2f56a356a1','2025-03-08'),(3,'Vignesh','Vignesh','V','student','vignesh@snulms.com','scrypt:32768:8:1$Z3P4CegSs2xK6Rcg$c4161379478a6cc373cef06986510d93aa851f756c53903266a25d74ee9a8d11a26a6ab34de1b40da2e8bf1bae4f4591a54f440bb84cdd9084b01e0bf6b80dbc','2025-03-08'),(4,'Vivesh','Vivesh','G','student','vivesh@snulms.com','scrypt:32768:8:1$UwITrHrhySZuBDeD$fd5c4d06ba455ba143ee4bf96ca512130ca589ecb7a0d85ae5073daa09fc34144f09870561f340899bd161efb89bc1e4e59918b17eddedd5969588d4b0bbdf39','2025-03-09');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-31 11:50:11
