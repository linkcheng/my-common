from django.db.models import *
import django.utils.timezone as timezone

from utils.encryptor import des_encryptor
from my_common.settings import (
    KAFKA_SERVERS,
    MYSQL_CONNECTOR_CLASS,
    MONGO_CONNECTOR_CLASS,
    TIME_ZONE
)


class Base(Model):

    class Meta:
        abstract = True

    id = AutoField('主键', primary_key=True)
    created_time = DateTimeField('创建时间', default=timezone.now)
    updated_time = DateTimeField('更新时间', auto_now=True)
    is_deleted = BooleanField('是否删除', default=False)


class _Database(Base):
    name = CharField(max_length=64, default='', verbose_name='数据库实例名称')
    username = CharField(max_length=32, default='', verbose_name='登录用户名')
    password = CharField(max_length=255, default='', verbose_name='登录密码')

    _password = None

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def hidden_password(self):
        return '******'

    def set_password(self, raw_password):
        self.password = des_encryptor.encrypt(raw_password)
        self._password = raw_password

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.password == self.hidden_password():
            fs = self._meta.fields
            update_fields = [f.attname for f in fs if not f.primary_key]
            update_fields.remove('password')
        else:
            self.set_password(self.password)
        super().save(force_insert, force_update, using, update_fields)


class Database(_Database):
    """
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
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='MySQL数据库配置';
    """
    host = CharField(max_length=128, default='', verbose_name='数据库地址')
    port = PositiveSmallIntegerField(default=3306, verbose_name='数据库端口号')

    class Meta:
        db_table = 'monitor_database'
        verbose_name = 'MySQL数据库配置'
        verbose_name_plural = verbose_name


class Mongo(_Database):
    """
    CREATE TABLE `monitor_mongo` (
      `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `name` varchar(64) NOT NULL DEFAULT '' COMMENT '数据库实例名称',
      `host` varchar(255) NOT NULL DEFAULT '' COMMENT '数据库地址',
      `username` varchar(32) NOT NULL DEFAULT '' COMMENT '登录用户名',
      `password` varchar(255) NOT NULL DEFAULT '' COMMENT '登录密码',
      `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否被删除，0否，1是',
      `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
      `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Mongo数据库配置';
    """
    host = CharField(max_length=255, default='', verbose_name='数据库地址')

    class Meta:
        db_table = 'monitor_mongo'
        verbose_name = 'Mongo数据库配置'
        verbose_name_plural = verbose_name


class MySQLConnector(Base):
    """
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

    """
    name = CharField(max_length=64, db_index=True, default='',
                     verbose_name='连接器名称')
    connector_class = CharField(max_length=128, default=MYSQL_CONNECTOR_CLASS,
                                verbose_name='连接器类')
    tasks_max = PositiveSmallIntegerField(default=1, verbose_name='最大任务数')
    history_kafka_topic = CharField(max_length=255, default='',
                                    verbose_name='历史记录恢复 topic',
                                    help_text='确保已经创建')
    history_kafka_servers = CharField(max_length=1024, default=KAFKA_SERVERS,
                                      verbose_name='用于恢复的 kafka 集群地址')

    # 监听的数据库相关配置
    database = ForeignKey('Database', related_name='database',
                          on_delete=CASCADE, verbose_name='连接的目标数据库')
    server_id = PositiveIntegerField(verbose_name='数据库唯一标识')
    # 逻辑名称，用于标识特定的MySQL数据库服务器/集群并为其提供名称空间。
    # 逻辑名称在所有其他连接器上都应该是唯一的，因为它用作该连接器发出的所有Kafka主题名称的前缀。
    server_name = CharField(max_length=128, default='',
                            verbose_name='连接器中数据库对应名称')
    schema_whitelist = CharField(max_length=255, default='', blank=True,
                                 verbose_name='库白名单',
                                 help_text='逗号分隔的正则表达式列表')
    schema_blacklist = CharField(max_length=255, default='', blank=True,
                                 verbose_name='库黑名单',
                                 help_text='逗号分隔的正则表达式列表，黑白名单不同时生效')
    table_whitelist = CharField(max_length=255, default='', blank=True,
                                verbose_name='表白名单',
                                help_text='逗号分隔的正则表达式列表')
    table_blacklist = CharField(max_length=255, default='', blank=True,
                                verbose_name='表黑名单',
                                help_text='逗号分隔的正则表达式列表，黑白名单不同时生效')
    include_schema_changes = BooleanField(default=False,
                                          verbose_name='是否监听DDL语句')
    """
    UNASSIGNED: The connector/task has not yet been assigned to a worker.
    RUNNING: The connector/task is running.
    PAUSED: The connector/task has been administratively paused.
    FAILED: The connector/task has failed (usually by raising an exception, 
            which is reported in the status output).
    """
    status = CharField(max_length=16, default='', verbose_name='连接器状态')

    is_deleted = PositiveSmallIntegerField(default=0,
                                           verbose_name='是否删除: 0是，其他否')

    class Meta:
        db_table = 'monitor_mysql_connector'
        verbose_name = 'MySQL连接器'
        verbose_name_plural = verbose_name

        unique_together = (
            ('server_id', 'is_deleted'),
            ('server_name', 'is_deleted'),
        )

        permissions = (
            ('read_mysql_connector', 'Can view MySQL connector'),
            ('write_mysql_connector', 'Can update MySQL connector'),
        )

    def __str__(self):
        return self.name

    def get_config(self):
        config = {
            "connector.class": self.connector_class,
            "tasks.max": self.tasks_max,
            "database.hostname": self.database.host,
            "database.port": str(self.database.port),
            "database.user": self.database.username,
            "database.password": des_encryptor.decrypt(self.database.password),
            "database.server.id": str(self.server_id),
            "database.server.name": self.server_name,
            "database.serverTimezone": TIME_ZONE,
            "database.history.kafka.bootstrap.servers": self.history_kafka_servers,
            "database.history.kafka.topic": self.history_kafka_topic,
            "include.schema.changes": "true" if self.include_schema_changes else "false",
        }

        filter_config = {}
        if self.schema_whitelist:
            filter_config["database.whitelist"] = self.schema_whitelist
        elif self.schema_blacklist:
            filter_config["database.blacklist"] = self.schema_blacklist

        if self.table_whitelist:
            filter_config["table.whitelist"] = self.table_whitelist
        elif self.table_blacklist:
            filter_config["table.blacklist"] = self.table_blacklist

        if filter_config:
            config.update(filter_config)

        return config


class MongoConnector(Base):
    """
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

    """
    name = CharField(max_length=64, db_index=True, default='',
                     verbose_name='连接器名称')
    connector_class = CharField(max_length=128, default=MONGO_CONNECTOR_CLASS,
                                verbose_name='连接器类')
    tasks_max = PositiveSmallIntegerField(default=1, verbose_name='最大任务数')

    # 监听的数据库相关配置
    database = ForeignKey('Mongo', related_name='database',
                          on_delete=CASCADE, verbose_name='连接的目标数据库')
    # 唯一名称，用于标识该连接器监视的连接器和/或MongoDB副本集或分片群集。
    # 每个服务器最多应由一个Debezium连接器监视，因为它用作该连接器发出的所有Kafka主题名称的前缀。
    server_name = CharField(max_length=128, default='',
                            verbose_name='连接器中数据库对应名称')
    database_whitelist = CharField(max_length=255, default='', blank=True,
                                   verbose_name='库白名单',
                                   help_text='逗号分隔的正则表达式列表')
    database_blacklist = CharField(max_length=255, default='', blank=True,
                                   verbose_name='库黑名单',
                                   help_text='逗号分隔的正则表达式列表，黑白名单不同时生效')
    collection_whitelist = CharField(max_length=255, default='', blank=True,
                                     verbose_name='集合白名单',
                                     help_text='逗号分隔的正则表达式列表')
    collection_blacklist = CharField(max_length=255, default='', blank=True,
                                     verbose_name='集合黑名单',
                                     help_text='逗号分隔的正则表达式列表，黑白名单不同时生效')

    """
    UNASSIGNED: The connector/task has not yet been assigned to a worker.
    RUNNING: The connector/task is running.
    PAUSED: The connector/task has been administratively paused.
    FAILED: The connector/task has failed (usually by raising an exception, 
            which is reported in the status output).
    """
    status = CharField(max_length=16, default='', verbose_name='连接器状态')

    is_deleted = PositiveSmallIntegerField(default=0,
                                           verbose_name='是否删除: 0是，其他否')

    class Meta:
        db_table = 'monitor_mongo_connector'
        verbose_name = 'Mongo连接器'
        verbose_name_plural = verbose_name

        unique_together = (
            ('server_name', 'is_deleted'),
        )

        permissions = (
            ('read_mongo_connector', 'Can view Mongo connector'),
            ('write_mongo_connector', 'Can update Mongo connector'),
        )

    def __str__(self):
        return self.name

    def get_config(self):
        config = {
            "connector.class": self.connector_class,
            "tasks.max": self.tasks_max,
            "mongodb.name": self.server_name,
            "mongodb.hosts": self.database.host,
            "mongodb.user": self.database.username,
            "mongodb.password": des_encryptor.decrypt(self.database.password),
        }

        filter_config = {}
        if self.database_whitelist:
            filter_config["database.whitelist"] = self.database_whitelist
        elif self.database_blacklist:
            filter_config["database.blacklist"] = self.database_blacklist

        if self.collection_whitelist:
            filter_config["collection.whitelist"] = self.collection_whitelist
        elif self.collection_blacklist:
            filter_config["collection.blacklist"] = self.collection_blacklist

        if filter_config:
            config.update(filter_config)

        return config
