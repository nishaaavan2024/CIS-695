CREATE DATABASE `timesheet` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;


CREATE TABLE `timesheet` (
  `idtimesheet` int NOT NULL AUTO_INCREMENT,
  `username` varchar(45) NOT NULL,
  `employeeid` int NOT NULL,
  `startdatetime` datetime NOT NULL,
  `enddatetime` datetime NOT NULL,
  `hours` decimal(10,0) DEFAULT NULL,
  `breakinminutes` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`idtimesheet`),
  UNIQUE KEY `timesheetdata` (`username`,`employeeid`,`startdatetime`,`enddatetime`),
  KEY `usernamefk_idx` (`username`),
  KEY `employeeid_idx` (`employeeid`) /*!80000 INVISIBLE */,
  CONSTRAINT `employeeidfk` FOREIGN KEY (`employeeid`) REFERENCES `users` (`employeeid`),
  CONSTRAINT `usernamefk` FOREIGN KEY (`username`) REFERENCES `users` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `users` (
  `idusers` int NOT NULL AUTO_INCREMENT,
  `username` varchar(45) NOT NULL,
  `employeeid` int NOT NULL,
  `firstname` varchar(45) DEFAULT NULL,
  `lastname` varchar(45) DEFAULT NULL,
  `status` varchar(45) DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`idusers`),
  UNIQUE KEY `username_UNIQUE` (`username`),
  UNIQUE KEY `employeeid_UNIQUE` (`employeeid`),
  UNIQUE KEY `idusers_UNIQUE` (`idusers`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
