-- MySQL dump 10.17  Distrib 10.3.23-MariaDB, for debian-linux-gnueabihf (armv7l)
--
-- Host: localhost    Database: emoncms
-- ------------------------------------------------------
-- Server version	10.3.23-MariaDB-0+deb10u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `app_config`
--

DROP TABLE IF EXISTS `app_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_config` (
  `userid` int(11) DEFAULT NULL,
  `data` text DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_config`
--

LOCK TABLES `app_config` WRITE;
/*!40000 ALTER TABLE `app_config` DISABLE KEYS */;
/*!40000 ALTER TABLE `app_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dashboard`
--

DROP TABLE IF EXISTS `dashboard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userid` int(11) DEFAULT NULL,
  `content` text DEFAULT NULL,
  `height` int(11) DEFAULT 600,
  `name` varchar(30) DEFAULT 'no name',
  `alias` varchar(20) DEFAULT '',
  `description` varchar(255) DEFAULT 'no description',
  `main` tinyint(1) DEFAULT 0,
  `public` tinyint(1) DEFAULT 0,
  `published` tinyint(1) DEFAULT 0,
  `showdescription` tinyint(1) DEFAULT 0,
  `backgroundcolor` varchar(6) DEFAULT 'EDF7FC',
  `gridsize` tinyint(1) DEFAULT 20,
  `fullscreen` tinyint(1) DEFAULT 0,
  `feedmode` varchar(8) DEFAULT 'feedid',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dashboard`
--

LOCK TABLES `dashboard` WRITE;
/*!40000 ALTER TABLE `dashboard` DISABLE KEYS */;
/*!40000 ALTER TABLE `dashboard` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `demandshaper`
--

DROP TABLE IF EXISTS `demandshaper`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `demandshaper` (
  `userid` int(11) DEFAULT NULL,
  `schedules` text DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `demandshaper`
--

LOCK TABLES `demandshaper` WRITE;
/*!40000 ALTER TABLE `demandshaper` DISABLE KEYS */;
/*!40000 ALTER TABLE `demandshaper` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device`
--

DROP TABLE IF EXISTS `device`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userid` int(11) DEFAULT NULL,
  `nodeid` text DEFAULT NULL,
  `name` text DEFAULT NULL,
  `description` text DEFAULT NULL,
  `type` varchar(32) DEFAULT NULL,
  `devicekey` varchar(64) DEFAULT NULL,
  `time` int(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device`
--

LOCK TABLES `device` WRITE;
/*!40000 ALTER TABLE `device` DISABLE KEYS */;
INSERT INTO `device` VALUES (1,1,'emonpi','emonpi','','','',NULL),(2,1,'TRH12220020','TRH12220020','','','',NULL),(5,1,'TEXT12310257','TEXT12310257','','','',NULL),(6,1,'circuits_PT100','circuits_PT100','','','',NULL),(7,1,'emontx1','emontx1','','','',NULL),(8,1,'TRH12220041','TRH12220041','','','',NULL),(11,1,'TRH12220064','TRH12220064','','','',NULL),(10,1,'TRH12220046','TRH12220046','','','',NULL);
/*!40000 ALTER TABLE `device` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feeds`
--

DROP TABLE IF EXISTS `feeds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `feeds` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text DEFAULT NULL,
  `userid` int(11) DEFAULT NULL,
  `tag` text DEFAULT NULL,
  `time` int(10) DEFAULT NULL,
  `value` double DEFAULT NULL,
  `datatype` int(11) NOT NULL,
  `public` tinyint(1) DEFAULT 0,
  `size` int(11) DEFAULT NULL,
  `engine` int(11) NOT NULL DEFAULT 0,
  `server` int(11) NOT NULL DEFAULT 0,
  `processList` text DEFAULT NULL,
  `unit` varchar(10) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=25 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feeds`
--

LOCK TABLES `feeds` WRITE;
/*!40000 ALTER TABLE `feeds` DISABLE KEYS */;
INSERT INTO `feeds` VALUES (1,'VAN_Text',1,'sofrel_Vantage',NULL,NULL,1,0,11381696,5,0,NULL,''),(2,'VAN_ray_sol',1,'sofrel_Vantage',NULL,NULL,1,0,11381668,5,0,NULL,''),(3,'temp',1,'bureauAC',NULL,NULL,1,0,226752,5,0,NULL,'°C'),(4,'timer',1,'TEXT12310257',NULL,NULL,1,1,114068,5,0,NULL,''),(5,'temp',1,'TEXT12310257',NULL,NULL,1,1,114068,5,0,NULL,'°C'),(6,'pwr1_PP2_SUD',1,'emontx1',NULL,NULL,1,1,114068,5,0,NULL,'W'),(7,'TimerB101zikNORD',1,'TRH12220020',NULL,NULL,1,1,114064,5,0,NULL,''),(8,'tempB101zikNORD',1,'TRH12220020',NULL,NULL,1,1,114064,5,0,NULL,'°C'),(9,'humB101zikNORD',1,'TRH12220020',NULL,NULL,1,1,114064,5,0,NULL,'%'),(10,'TimerB209technoNORD',1,'TRH12220041',NULL,NULL,1,1,114064,5,0,NULL,''),(11,'tempB209technoNORD',1,'TRH12220041',NULL,NULL,1,1,114064,5,0,NULL,'°C'),(12,'humB209technoNORD',1,'TRH12220041',NULL,NULL,1,1,114060,5,0,NULL,'%'),(13,'TimerB216SUD',1,'TRH12220046',NULL,NULL,1,1,114060,5,0,NULL,''),(14,'tempB216SUD',1,'TRH12220046',NULL,NULL,1,1,114060,5,0,NULL,'°C'),(15,'humB216SUD',1,'TRH12220046',NULL,NULL,1,1,114060,5,0,NULL,'%'),(16,'TimerB140artSUD',1,'TRH12220064',NULL,NULL,1,1,114060,5,0,NULL,''),(17,'tempB140artSUD',1,'TRH12220064',NULL,NULL,1,1,114060,5,0,NULL,'°C'),(18,'humB140artSUD',1,'TRH12220064',NULL,NULL,1,1,114060,5,0,NULL,'%'),(19,'PT100_1_depSUD',1,'circuits_PT100',NULL,NULL,1,1,114060,5,0,NULL,'°C'),(20,'PT100_2_retSUD',1,'circuits_PT100',NULL,NULL,1,1,114060,5,0,NULL,'°C'),(21,'PT100_3_depNORD',1,'circuits_PT100',NULL,NULL,1,1,114060,5,0,NULL,'°C'),(22,'PT100_4_retNORD',1,'circuits_PT100',NULL,NULL,1,1,114060,5,0,NULL,'°C'),(23,'pwr2_PP2_NORD',1,'emontx1',NULL,NULL,1,1,114056,5,0,NULL,'W'),(24,'t1_sousstation',1,'emonpi',NULL,NULL,1,1,114056,5,0,NULL,'°C');
/*!40000 ALTER TABLE `feeds` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `graph`
--

DROP TABLE IF EXISTS `graph`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `graph` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userid` int(11) DEFAULT NULL,
  `groupid` int(11) DEFAULT 0,
  `data` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `graph`
--

LOCK TABLES `graph` WRITE;
/*!40000 ALTER TABLE `graph` DISABLE KEYS */;
INSERT INTO `graph` VALUES (1,1,0,'{\"name\":\"circuitSUD_aileOuest\",\"start\":1612296000000,\"end\":1612902600000,\"interval\":900,\"mode\":\"interval\",\"fixinterval\":false,\"floatingtime\":1,\"yaxismin\":\"auto\",\"yaxismax\":\"auto\",\"yaxismin2\":\"auto\",\"yaxismax2\":\"auto\",\"showmissing\":false,\"showtag\":true,\"showlegend\":true,\"showcsv\":0,\"csvtimeformat\":\"datestr\",\"csvnullvalues\":\"show\",\"csvheaders\":\"showNameTag\",\"feedlist\":[{\"id\":6,\"name\":\"pwr1_PP2_SUD\",\"tag\":\"emontx1\",\"yaxis\":2,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":0,\"plottype\":\"lines\",\"postprocessed\":true,\"color\":\"#ff80c0\"},{\"id\":19,\"name\":\"PT100_1_depSUD\",\"tag\":\"circuits_PT100\",\"yaxis\":1,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":1,\"plottype\":\"lines\",\"postprocessed\":true,\"color\":\"#ff0000\"},{\"id\":20,\"name\":\"PT100_2_retSUD\",\"tag\":\"circuits_PT100\",\"yaxis\":1,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":0,\"plottype\":\"lines\",\"postprocessed\":true,\"color\":\"#00ff00\"},{\"id\":5,\"name\":\"temp\",\"tag\":\"TEXT12310257\",\"yaxis\":1,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":1,\"plottype\":\"lines\",\"postprocessed\":true,\"color\":\"#0080ff\"}],\"id\":\"1\"}'),(2,1,0,'{\"name\":\"indoor_temps\",\"start\":1612252800000,\"end\":1612858500000,\"interval\":900,\"mode\":\"interval\",\"fixinterval\":false,\"floatingtime\":1,\"yaxismin\":\"auto\",\"yaxismax\":\"auto\",\"yaxismin2\":\"auto\",\"yaxismax2\":\"auto\",\"showmissing\":false,\"showtag\":true,\"showlegend\":true,\"showcsv\":0,\"csvtimeformat\":\"datestr\",\"csvnullvalues\":\"show\",\"csvheaders\":\"showNameTag\",\"feedlist\":[{\"id\":14,\"name\":\"tempB216SUD\",\"tag\":\"TRH12220046\",\"yaxis\":1,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":\"1\",\"plottype\":\"lines\",\"postprocessed\":true,\"color\":\"#ff8000\"},{\"id\":17,\"name\":\"tempB140artSUD\",\"tag\":\"TRH12220064\",\"yaxis\":1,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":1,\"plottype\":\"lines\",\"postprocessed\":true,\"color\":\"#ffcaca\"},{\"id\":11,\"name\":\"tempB209technoNORD\",\"tag\":\"TRH12220041\",\"yaxis\":1,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":1,\"plottype\":\"lines\",\"postprocessed\":true,\"color\":\"#80ff80\"},{\"id\":8,\"name\":\"tempB101zikNORD\",\"tag\":\"TRH12220020\",\"yaxis\":1,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":1,\"plottype\":\"lines\",\"postprocessed\":true,\"color\":\"#008000\"}],\"id\":\"2\"}'),(3,1,0,'{\"name\":\"circuitNORD_aileOuest\",\"start\":1612296900000,\"end\":1612902600000,\"interval\":900,\"mode\":\"interval\",\"fixinterval\":false,\"floatingtime\":1,\"yaxismin\":\"auto\",\"yaxismax\":\"auto\",\"yaxismin2\":\"auto\",\"yaxismax2\":\"auto\",\"showmissing\":false,\"showtag\":true,\"showlegend\":true,\"showcsv\":0,\"csvtimeformat\":\"datestr\",\"csvnullvalues\":\"show\",\"csvheaders\":\"showNameTag\",\"feedlist\":[{\"id\":23,\"name\":\"pwr2_PP2_NORD\",\"tag\":\"emontx1\",\"yaxis\":2,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":0,\"plottype\":\"lines\",\"postprocessed\":true,\"color\":\"#ff80c0\"},{\"id\":21,\"name\":\"PT100_3_depNORD\",\"tag\":\"circuits_PT100\",\"yaxis\":1,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":1,\"plottype\":\"lines\",\"postprocessed\":true,\"color\":\"#ff0000\"},{\"id\":22,\"name\":\"PT100_4_retNORD\",\"tag\":\"circuits_PT100\",\"yaxis\":1,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":0,\"plottype\":\"lines\",\"postprocessed\":true,\"color\":\"#00ff00\"},{\"id\":5,\"name\":\"temp\",\"tag\":\"TEXT12310257\",\"yaxis\":1,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":1,\"plottype\":\"lines\",\"postprocessed\":true,\"color\":\"#0000ff\"}],\"id\":\"3\"}'),(4,1,0,'{\"name\":\"NORD_circVSindoor\",\"start\":1615220100000,\"end\":1615825800000,\"interval\":900,\"mode\":\"interval\",\"fixinterval\":false,\"floatingtime\":1,\"yaxismin\":\"auto\",\"yaxismax\":\"auto\",\"yaxismin2\":\"auto\",\"yaxismax2\":\"auto\",\"showmissing\":false,\"showtag\":true,\"showlegend\":true,\"showcsv\":0,\"csvtimeformat\":\"datestr\",\"csvnullvalues\":\"show\",\"csvheaders\":\"showNameTag\",\"feedlist\":[{\"id\":8,\"name\":\"tempB101zikNORD\",\"tag\":\"TRH12220020\",\"yaxis\":2,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":1,\"plottype\":\"lines\",\"postprocessed\":true},{\"id\":11,\"name\":\"tempB209technoNORD\",\"tag\":\"TRH12220041\",\"yaxis\":2,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":0,\"plottype\":\"lines\",\"postprocessed\":true},{\"id\":21,\"name\":\"PT100_3_depNORD\",\"tag\":\"circuits_PT100\",\"yaxis\":1,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":1,\"plottype\":\"lines\",\"postprocessed\":true},{\"id\":22,\"name\":\"PT100_4_retNORD\",\"tag\":\"circuits_PT100\",\"yaxis\":1,\"fill\":0,\"scale\":1,\"offset\":0,\"delta\":false,\"getaverage\":false,\"dp\":1,\"plottype\":\"lines\",\"postprocessed\":true}],\"id\":\"\"}'),(5,1,0,'{\"name\":\"SUD_circVSindoor\",\"start\":1615220100000,\"end\":1615825800000,\"interval\":900,\"mode\":\"interval\",\"fixinterval\":false,\"floatingtime\":1,\"yaxismin\":\"auto\",\"yaxismax\":\"auto\",\"yaxismin2\":\"auto\",\"yaxismax2\":\"auto\",\"showmissing\":false,\"showtag\":true,\"showlegend\":true,\"showcsv\":0,\"csvtimeformat\":\"datestr\",\"csvnullvalues\":\"show\",\"csvheaders\":\"showNameTag\",\"feedlist\":[{\"id\":14,\"name\":\"tempB216SUD\",\"tag\":\"TRH12220046\",\"yaxis\":2,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":1,\"plottype\":\"lines\",\"postprocessed\":true},{\"id\":17,\"name\":\"tempB140artSUD\",\"tag\":\"TRH12220064\",\"yaxis\":2,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":1,\"plottype\":\"lines\",\"postprocessed\":true},{\"id\":19,\"name\":\"PT100_1_depSUD\",\"tag\":\"circuits_PT100\",\"yaxis\":1,\"fill\":0,\"scale\":\"1\",\"offset\":\"0\",\"delta\":false,\"getaverage\":false,\"dp\":1,\"plottype\":\"lines\",\"postprocessed\":true},{\"id\":20,\"name\":\"PT100_2_retSUD\",\"tag\":\"circuits_PT100\",\"yaxis\":1,\"fill\":0,\"scale\":1,\"offset\":0,\"delta\":false,\"getaverage\":false,\"dp\":0,\"plottype\":\"lines\",\"postprocessed\":true}],\"id\":\"\"}');
/*!40000 ALTER TABLE `graph` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `input`
--

DROP TABLE IF EXISTS `input`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `input` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userid` int(11) DEFAULT NULL,
  `nodeid` text DEFAULT NULL,
  `name` text DEFAULT NULL,
  `description` text DEFAULT NULL,
  `processList` text DEFAULT NULL,
  `time` int(10) DEFAULT NULL,
  `value` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=167 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `input`
--

LOCK TABLES `input` WRITE;
/*!40000 ALTER TABLE `input` DISABLE KEYS */;
INSERT INTO `input` VALUES (1,1,'emonpi','power1','','',NULL,NULL),(2,1,'emonpi','power2','','',NULL,NULL),(3,1,'emonpi','power1pluspower2','','',NULL,NULL),(4,1,'emonpi','vrms','','',NULL,NULL),(5,1,'emonpi','t1','','1:24',NULL,NULL),(6,1,'emonpi','t2','','',NULL,NULL),(7,1,'emonpi','t3','','',NULL,NULL),(8,1,'emonpi','t4','','',NULL,NULL),(9,1,'emonpi','t5','','',NULL,NULL),(10,1,'emonpi','t6','','',NULL,NULL),(11,1,'emonpi','pulsecount','','',NULL,NULL),(113,1,'emonpi','rssi','','',NULL,NULL),(13,1,'TRH12220020','SlaveType','','',NULL,NULL),(14,1,'TRH12220020','Timer','','1:7',NULL,NULL),(15,1,'TRH12220020','RSSI','','',NULL,NULL),(16,1,'TRH12220020','serHigh','','',NULL,NULL),(17,1,'TRH12220020','serLow','','',NULL,NULL),(18,1,'TRH12220020','temp','','1:3,1:8',NULL,NULL),(19,1,'TRH12220020','hum','','1:9',NULL,NULL),(77,1,'emontx1','power1','','1:6',NULL,NULL),(78,1,'emontx1','power2','','1:23',NULL,NULL),(79,1,'emontx1','power3','','',NULL,NULL),(80,1,'emontx1','power4','','',NULL,NULL),(81,1,'emontx1','vrms','','',NULL,NULL),(82,1,'emontx1','temp1','','',NULL,NULL),(76,1,'circuits_PT100','PT100_4','','1:22',NULL,NULL),(75,1,'circuits_PT100','PT100_3','','1:21',NULL,NULL),(74,1,'circuits_PT100','PT100_2','','1:20',NULL,NULL),(73,1,'circuits_PT100','PT100_1','','1:19',NULL,NULL),(72,1,'circuits_PT100','serial','','',NULL,NULL),(71,1,'TEXT12310257','slavetype','','',NULL,NULL),(70,1,'TEXT12310257','timer','','1:4',NULL,NULL),(69,1,'TEXT12310257','temp','','1:5',NULL,NULL),(68,1,'TEXT12310257','serLow','','',NULL,NULL),(67,1,'TEXT12310257','serHigh','','',NULL,NULL),(66,1,'TEXT12310257','RSSI','','',NULL,NULL),(83,1,'emontx1','temp2','','',NULL,NULL),(84,1,'emontx1','rssi','','',NULL,NULL),(85,1,'TRH12220041','RSSI','','',NULL,NULL),(86,1,'TRH12220041','serHigh','','',NULL,NULL),(87,1,'TRH12220041','serLow','','',NULL,NULL),(88,1,'TRH12220041','temp','','1:11',NULL,NULL),(89,1,'TRH12220041','hum','','1:12',NULL,NULL),(90,1,'TRH12220041','Timer','','1:10',NULL,NULL),(91,1,'TRH12220041','SlaveType','','',NULL,NULL),(110,1,'TRH12220064','serLow','','',NULL,NULL),(109,1,'TRH12220064','serHigh','','',NULL,NULL),(108,1,'TRH12220064','RSSI','','',NULL,NULL),(107,1,'TRH12220064','Timer','','1:16',NULL,NULL),(106,1,'TRH12220064','SlaveType','','',NULL,NULL),(99,1,'TRH12220046','SlaveType','','',NULL,NULL),(100,1,'TRH12220046','Timer','','1:13',NULL,NULL),(101,1,'TRH12220046','RSSI','','',NULL,NULL),(102,1,'TRH12220046','serHigh','','',NULL,NULL),(103,1,'TRH12220046','serLow','','',NULL,NULL),(104,1,'TRH12220046','temp','','1:14',NULL,NULL),(105,1,'TRH12220046','hum','','1:15',NULL,NULL),(111,1,'TRH12220064','temp','','1:17',NULL,NULL),(112,1,'TRH12220064','hum','','1:18',NULL,NULL);
/*!40000 ALTER TABLE `input` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `multigraph`
--

DROP TABLE IF EXISTS `multigraph`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `multigraph` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text DEFAULT NULL,
  `userid` int(11) DEFAULT NULL,
  `feedlist` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `multigraph`
--

LOCK TABLES `multigraph` WRITE;
/*!40000 ALTER TABLE `multigraph` DISABLE KEYS */;
/*!40000 ALTER TABLE `multigraph` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `postprocess`
--

DROP TABLE IF EXISTS `postprocess`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `postprocess` (
  `userid` int(11) DEFAULT NULL,
  `data` text DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `postprocess`
--

LOCK TABLES `postprocess` WRITE;
/*!40000 ALTER TABLE `postprocess` DISABLE KEYS */;
INSERT INTO `postprocess` VALUES (1,'[]');
/*!40000 ALTER TABLE `postprocess` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rememberme`
--

DROP TABLE IF EXISTS `rememberme`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rememberme` (
  `userid` int(11) DEFAULT NULL,
  `token` varchar(40) DEFAULT NULL,
  `persistentToken` varchar(40) DEFAULT NULL,
  `expire` datetime DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rememberme`
--

LOCK TABLES `rememberme` WRITE;
/*!40000 ALTER TABLE `rememberme` DISABLE KEYS */;
INSERT INTO `rememberme` VALUES (1,'22dc2359636f521e54772095f680a171768fe9bb','f20b4124bf0103364d4fdf71dd502f34f2f0fce9','2021-05-13 20:06:54');
/*!40000 ALTER TABLE `rememberme` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schedule`
--

DROP TABLE IF EXISTS `schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `schedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userid` int(11) DEFAULT NULL,
  `name` varchar(30) DEFAULT NULL,
  `expression` text DEFAULT NULL,
  `timezone` varchar(64) DEFAULT 'UTC',
  `public` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schedule`
--

LOCK TABLES `schedule` WRITE;
/*!40000 ALTER TABLE `schedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `schedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `setup`
--

DROP TABLE IF EXISTS `setup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `setup` (
  `state` varchar(32) DEFAULT 'unconfigured',
  `wifi` varchar(32) DEFAULT 'unconfigured'
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `setup`
--

LOCK TABLES `setup` WRITE;
/*!40000 ALTER TABLE `setup` DISABLE KEYS */;
INSERT INTO `setup` VALUES ('unconfigured','ethernet');
/*!40000 ALTER TABLE `setup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sync`
--

DROP TABLE IF EXISTS `sync`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sync` (
  `userid` int(11) DEFAULT NULL,
  `host` varchar(64) DEFAULT NULL,
  `username` varchar(30) DEFAULT NULL,
  `apikey_read` varchar(64) DEFAULT NULL,
  `apikey_write` varchar(64) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sync`
--

LOCK TABLES `sync` WRITE;
/*!40000 ALTER TABLE `sync` DISABLE KEYS */;
INSERT INTO `sync` VALUES (1,'http://allierhab.ddns.net','alexandrecuer','8f87b1d04209ac8771a688c86ae245c9','9237c4290003ddb9c240730eecc9d4ff');
/*!40000 ALTER TABLE `sync` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) DEFAULT NULL,
  `email` varchar(64) DEFAULT NULL,
  `password` varchar(64) DEFAULT NULL,
  `salt` varchar(32) DEFAULT NULL,
  `apikey_write` varchar(64) DEFAULT NULL,
  `apikey_read` varchar(64) DEFAULT NULL,
  `lastlogin` datetime DEFAULT NULL,
  `admin` int(11) NOT NULL,
  `gravatar` varchar(30) DEFAULT '',
  `name` varchar(30) DEFAULT '',
  `location` varchar(30) DEFAULT '',
  `timezone` varchar(64) DEFAULT 'UTC',
  `language` varchar(5) DEFAULT 'en_EN',
  `bio` text DEFAULT NULL,
  `tags` text DEFAULT NULL,
  `startingpage` varchar(64) DEFAULT 'feed/list',
  `email_verified` int(11) DEFAULT 0,
  `verification_key` varchar(64) DEFAULT '',
  `preferences` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'verdi','alexandre.cuer@cerema.fr','adf05ba7047c58850dc714e2a43b223b3e5a8002573cbe49de343fab184638d0','1e7b2414656e8ff13e3fe869b427e26e','9244a4fc9def8a9c09889aba2862705b','7d7c89f723d5da7d2a021366994510cb',NULL,1,'','','','Europe/Paris','en_EN',NULL,NULL,'feed/list',0,'','{\"0\":false,\"bookmarks\":[{\"path\":\"graph\\/1604469604\",\"text\":\" Graphs  \"}]}');
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

-- Dump completed on 2021-05-24 13:38:28
