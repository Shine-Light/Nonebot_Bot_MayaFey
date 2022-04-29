-- --------------------------------------------------------
-- 主机:                           127.0.0.1
-- 服务器版本:                        10.4.20-MariaDB - mariadb.org binary distribution
-- 服务器操作系统:                      Win64
-- HeidiSQL 版本:                  11.3.0.6295
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- 导出 mayafey 的数据库结构
CREATE DATABASE IF NOT EXISTS `mayafey` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin */;
USE `mayafey`;

-- 导出  表 mayafey.credit 结构
CREATE TABLE IF NOT EXISTS `credit` (
  `gid` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '群号',
  `uid` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'QQ号',
  `credit` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin COMMENT='积分表';

-- 数据导出被取消选择。

-- 导出  表 mayafey.sign 结构
CREATE TABLE IF NOT EXISTS `sign` (
  `gid` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '群号',
  `uid` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'QQ号',
  `date_last` date DEFAULT NULL COMMENT '最后签到日期',
  `count_all` int(10) unsigned DEFAULT NULL COMMENT '签到总数',
  `count_continue` int(10) unsigned DEFAULT NULL COMMENT '连续签到数'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin COMMENT='签到表';

-- 数据导出被取消选择。

-- 导出  表 mayafey.users 结构
CREATE TABLE IF NOT EXISTS `users` (
  `gid` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '群号',
  `uid` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL COMMENT 'QQ号',
  `role` varchar(20) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '身份',
  `ban_count` tinyint(3) unsigned DEFAULT NULL COMMENT '违禁次数',
  `alive` tinyint(1) DEFAULT NULL COMMENT '是否还在群中'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin COMMENT='用户表';

-- 数据导出被取消选择。

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
