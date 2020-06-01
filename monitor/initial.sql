
-- Mongo 连接器
DROP TABLE IF EXISTS monitor_mysql_connector;
CREATE TABLE `monitor_mongo_connector` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL DEFAULT '' COMMENT '连接器名称',
  `connector_class` varchar(128) NOT NULL DEFAULT '' COMMENT '连接器类',
  `tasks_max` smallint(6) unsigned NOT NULL DEFAULT '1' COMMENT '最大任务数',
  `database_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '连接的 MongoDB 数据库',
  `server_name` varchar(128) NOT NULL DEFAULT '' COMMENT '连接器中数据库对应名称',
  `database_whitelist` varchar(255) NOT NULL DEFAULT '' COMMENT '库白名单',
  `database_blacklist` varchar(255) NOT NULL DEFAULT '' COMMENT '库黑名单',
  `collection_whitelist` varchar(255) NOT NULL DEFAULT '' COMMENT '集合白名单',
  `collection_blacklist` varchar(255) NOT NULL DEFAULT '' COMMENT '集合黑名单',
  `status` varchar(16) NOT NULL DEFAULT '' COMMENT '连接器状态',
  `is_deleted` smallint(6) unsigned NOT NULL DEFAULT '0' COMMENT '是否删除: 0是，其他否',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY idx_name(`name`),
  UNIQUE KEY uniq_server_name_is_deleted(`server_name`, `is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Mongo连接器';

-- Mongo 数据库配置
DROP TABLE IF EXISTS monitor_mongo;
CREATE TABLE `monitor_mongo` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL DEFAULT '' COMMENT '数据库实例名称',
  `host` varchar(255) NOT NULL DEFAULT '' COMMENT '数据库host',
  `username` varchar(32) NOT NULL DEFAULT '' COMMENT '登录用户名',
  `password` varchar(255) NOT NULL DEFAULT '' COMMENT '登录密码',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否被删除，0否，1是',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Mongo数据库配置';


-- MySQL 连接器
DROP TABLE IF EXISTS monitor_mysql_connector;
CREATE TABLE `monitor_mysql_connector` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL DEFAULT '' COMMENT '连接器名称',
  `connector_class` varchar(128) NOT NULL DEFAULT '' COMMENT '连接器类',
  `tasks_max` smallint(6) unsigned NOT NULL DEFAULT '1' COMMENT '最大任务数',
  `history_kafka_topic` varchar(255) NOT NULL DEFAULT '' COMMENT '历史记录恢复 topic',
  `history_kafka_servers` varchar(1024) NOT NULL DEFAULT '' COMMENT '用于恢复的 kafka 集群地址',
  `database_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '连接的目标数据库',
  `server_id` int(11) unsigned NOT NULL DEFAULT '5500' COMMENT '数据库唯一标识',
  `server_name` varchar(128) NOT NULL DEFAULT '' COMMENT '连接器中数据库对应名称',
  `schema_whitelist` varchar(255) NOT NULL DEFAULT '' COMMENT '库白名单',
  `schema_blacklist` varchar(255) NOT NULL DEFAULT '' COMMENT '库黑名单',
  `table_whitelist` varchar(255) NOT NULL DEFAULT '' COMMENT '表白名单',
  `table_blacklist` varchar(255) NOT NULL DEFAULT '' COMMENT '表黑名单',
  `include_schema_changes` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否监听DDL语句',
  `status` varchar(16) NOT NULL DEFAULT '' COMMENT '连接器状态',
  `is_deleted` smallint(6) unsigned NOT NULL DEFAULT '0' COMMENT '是否删除: 0是，其他否',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY idx_name(`name`),
  UNIQUE KEY uniq_server_id_is_deleted(`server_id`, `is_deleted`),
  UNIQUE KEY uniq_server_name_is_deleted(`server_name`, `is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='MySQL连接器';




-- 数据库配置

-- MySQL 数据库配置

DROP TABLE IF EXISTS monitor_database;
CREATE TABLE `monitor_database` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL DEFAULT '' COMMENT '数据库实例名称',
  `host` varchar(128) NOT NULL DEFAULT '' COMMENT '数据库地址',
  `port` smallint(11) unsigned NOT NULL DEFAULT '3306' COMMENT '数据库端口号',
  `username` varchar(32) NOT NULL DEFAULT '' COMMENT '登录用户名',
  `password` varchar(255) NOT NULL DEFAULT '' COMMENT '登录密码',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否被删除，0否，1是',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据库配置';

