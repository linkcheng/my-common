-- 数据库配置
DROP TABLE IF EXISTS metadata_schema_config;
CREATE TABLE metadata_schema_config (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `database_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '数据库实例ID',
  `schema_name` varchar(64) NOT NULL DEFAULT '' COMMENT '数据库名称',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否被删除，0否，1是',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据库配置';


-- 数据库实例配置
DROP TABLE IF EXISTS metadata_database_config;
CREATE TABLE metadata_database_config (
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
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据库实例配置';


-- 数据表信息
DROP TABLE IF EXISTS metadata_table_info;
CREATE TABLE metadata_table_info (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `table_schema` varchar(64) NOT NULL DEFAULT '' COMMENT '数据库名称',
  `table_name` varchar(64) NOT NULL DEFAULT '' COMMENT '表名称',
  `table_comment` varchar(255) NOT NULL DEFAULT '' COMMENT '表备注',
  `table_collation` varchar(32) NOT NULL DEFAULT '' COMMENT '表字符校验编码集',
  `row_format` varchar(20) NOT NULL DEFAULT '' COMMENT '表行格式',
  `create_time` datetime DEFAULT NULL COMMENT '表创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '表更新时间',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否被删除，0否，1是',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_table_created_time_schema` (`table_name`, `created_time`, `table_schema`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据表信息';


-- 字段信息
DROP TABLE IF EXISTS metadata_column_info;
CREATE TABLE metadata_column_info (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `table_schema` varchar(64) NOT NULL DEFAULT '' COMMENT '数据库名称',
  `table_name` varchar(64) NOT NULL DEFAULT '' COMMENT '表名称',
  `column_name` varchar(64) NOT NULL DEFAULT '' COMMENT '列名称',
  `column_type` varchar(255) NOT NULL DEFAULT '' COMMENT '列类型',
  `is_nullable` varchar(3) NOT NULL DEFAULT '' COMMENT '列是否可以为空',
  `column_default` varchar(255) DEFAULT NULL COMMENT '列默认值',
  `extra` varchar(30) NOT NULL DEFAULT '' COMMENT '补充信息',
  `column_comment` varchar(1024) NOT NULL DEFAULT '' COMMENT '列备注',
  `ordinal_position` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '列序号',
  `character_set_name` varchar(32) DEFAULT NULL COMMENT '列字符集',
  `collation_name` varchar(32) DEFAULT NULL COMMENT '列字符校验编码集',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否被删除，0否，1是',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_column_created_time` (`column_name`, `created_time`),
  KEY `idx_table_created_time_schema` (`table_name`, `created_time`, `table_schema`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='字段信息';


-- 索引信息
DROP TABLE IF EXISTS metadata_statistics_info;
CREATE TABLE metadata_statistics_info (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `table_schema` varchar(64) NOT NULL DEFAULT '' COMMENT '数据库名称',
  `table_name` varchar(64) NOT NULL DEFAULT '' COMMENT '表名称',
  `index_name` varchar(64) NOT NULL DEFAULT '' COMMENT '索引名称',
  `column_name` varchar(64) NOT NULL COMMENT '列名',
  `seq_in_index` int(11) NOT NULL DEFAULT '0' COMMENT '索引列顺序',
  `index_type` varchar(16) NOT NULL DEFAULT '' COMMENT '索引类型',
  `index_comment` varchar(1024) NOT NULL DEFAULT '' COMMENT '索引备注',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否被删除，0否，1是',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_table_created_time_schema` (`table_name`, `created_time`, `table_schema`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='索引信息';


-- 评论
DROP TABLE IF EXISTS metadata_comment;
CREATE TABLE metadata_comment (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '用户ID',
  `table_schema` varchar(64) NOT NULL DEFAULT '' COMMENT '数据库名称',
  `table_name` varchar(64) NOT NULL DEFAULT '' COMMENT '表名称',
  `parent_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '被评论的ID',
  `content` text COMMENT '评论内容',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否被删除，0否，1是',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评论';
