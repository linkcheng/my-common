--
-- Create model common_date
--
DROP TABLE IF EXISTS `common_date`;
CREATE TABLE `common_date` (
    `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
    `date` date NOT NULL COMMENT '日期YYYYmmdd',
    `date_str` varchar(12) NOT NULL COMMENT '日期YYYYmmdd',
    `weekday` tinyint(1) NOT NULL COMMENT '星期: 星期一 0, 星期二 1, 星期三 2, 星期四 3, 星期五 4, 星期六 5, 星期日 6',
    `class` tinyint(1) NOT NULL DEFAULT 0 COMMENT '分类：工作日0，休息日1，节假日2',
    `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `unique_date_index` (`date`),
    UNIQUE KEY `unique_date_str_index` (`date_str`),
    KEY `update_time_index` (`updated_time`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='公共时间维度';
--
-- Create model common_number_attribution
--
DROP TABLE IF EXISTS `common_mobile_attribution`;
CREATE TABLE `common_mobile_attribution` (
    `id` int(11) AUTO_INCREMENT NOT NULL,
    `number` varchar(12) NOT NULL COMMENT '手机号码前7位',
    `zip_code` varchar(12) COMMENT '归属地邮编',
    `city_code` varchar(12) COMMENT '归属地区号',
    `full_province` varchar(16) COMMENT '归属地省份-全称',
    `full_city` varchar(16) COMMENT '归属地城市-全称',
    `short_province` varchar(16) COMMENT '归属地省份-简称',
    `short_city` varchar(16) COMMENT '归属地城市-简称',
    `phone_type` varchar(6) COMMENT '运营商分类：中国移动，中国联通，中国电信',
    `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `unique_number_index` (`number`),
    KEY `update_time_index` (`updated_time`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='手机号码归属地维度';
--
-- Create model common_id_card_number_attribution
--
DROP TABLE IF EXISTS `common_id_attribution`;
CREATE TABLE `common_id_attribution` (
    `id` int(11) AUTO_INCREMENT NOT NULL,
    `number` varchar(12) NOT NULL COMMENT '身份证号码前6位',
    `city_code` varchar(12) COMMENT '归属地区号',
    `full_province` varchar(16) NOT NULL COMMENT '归属地省份-全称',
    `full_city` varchar(16) COMMENT '归属地城市-全称',
    `full_district` varchar(16) COMMENT '归属地区县-全称',
    `short_province` varchar(16) NOT NULL COMMENT '归属地省份-简称',
    `short_city` varchar(16) COMMENT '归属地城市-简称',
    `short_district` varchar(16) COMMENT '归属地区县-简称',
    `level` varchar(12) NOT NULL COMMENT '行政等级 分类: province, city, district',
    `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `unique_number_index` (`number`),
    KEY `update_time_index` (`updated_time`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='身份证号归属地维度';
--
-- Create model common_gps
--
# DROP TABLE IF EXISTS `common_gps`;
# CREATE TABLE `common_gps` (
#     `id` int(11) AUTO_INCREMENT NOT NULL,
#     `district_name` varchar(7) NOT NULL COMMENT '行政区名字',
#     `class` tinyint(1) NOT NULL COMMENT '行政区级别分类：省级 0，地级市 1，县级 2',
#     `adcode` varchar(6) NOT NULL COMMENT '区域编码',
#     `city_code` varchar(4) COMMENT '城市编码',
#     `polygon` polygon COMMENT '行政区边界',
#     `parent_adcode` varchar(6) COMMENT '父级区域编码',
#     `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
#     `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
#     PRIMARY KEY (`id`),
#     KEY `adcode_index` (`adcode`)
# )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='GPS维度表';

