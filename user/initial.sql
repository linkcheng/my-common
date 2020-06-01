-- 用户组菜单对应表
DROP TABLE IF EXISTS user_group_menus;
CREATE TABLE `user_group_menus` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `group_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '用户组id',
  `menu_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '菜单id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户组菜单表';


-- 菜单表
DROP TABLE IF EXISTS user_menu;
CREATE TABLE `user_menu` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL DEFAULT '' COMMENT '菜单名称',
  `icon_code` varchar(64) NOT NULL DEFAULT '' COMMENT '菜单icon编码',
  `parent_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '是否有父菜单,0为顶级菜单',
  `order` int(11) NOT NULL  DEFAULT '0' COMMENT '菜单排序，数值越高排序越靠前',
  `menu_url` varchar(128) NOT NULL DEFAULT '#' COMMENT '菜单路由',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否被删除，0否，1是',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='菜单表';

-- 初始化数据
INSERT INTO `user_menu` (`name`, `icon_code`, `parent_id`, `order`, `menu_url`)
VALUES
('Dashboard', 'icon fa fa-tachometer', 0, 2000, '/dashboard/'),
('数据字典', 'icon fa fa-table', 0, 1000, '/metadata/search/'),
('公共维度', 'icon fa fa-cubes', 0, 900, '#'),
('日期维度', '', 3, 890, '/common/date/'),
('手机号归属地', '', 3, 880, '#'),
('身份证归属地', '', 3, 870, '#'),
('GPS归属地', '', 3, 860, '#'),
('菜单管理', 'icon fa fa-list-ul', 0, 200, '/user/menu/'),
('操作日志', 'icon fa fa-file-archive-o', 0, 100, '/user/log/');


-- 操作日志表
DROP TABLE IF EXISTS user_operation_log;
CREATE TABLE `user_operation_log` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(255) NOT NULL DEFAULT '' COMMENT '请求地址',
  `method` varchar(12) NOT NULL DEFAULT '' COMMENT '请求类型',
  `headers` text COMMENT '请求头',
  `body` text COMMENT '请求参数',
  `user_id` int(11) NOT NULL default '0' COMMENT '用户id',
  `username` varchar(64) NOT NULL default '' COMMENT '登录名',
  `user_agent` text COMMENT '客户端类型',
  `ip` varchar(15) NOT NULL DEFAULT '' COMMENT '操作ip',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否被删除，0否，1是',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_created_time_user_name` (`created_time`, username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志';