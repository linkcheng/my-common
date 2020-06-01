import logging
from django.db.models import *
import django.utils.timezone as timezone
from utils.encryptor import des_encryptor

logger = logging.getLogger(__name__)


class Base(Model):

    class Meta:
        abstract = True

    id = AutoField('主键', primary_key=True)
    created_time = DateTimeField('创建时间', default=timezone.now)
    updated_time = DateTimeField('更新时间', auto_now=True)
    is_deleted = BooleanField('是否删除', default=False)


class DatabaseConfig(Base):
    """
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
    """

    name = CharField(max_length=64, default='', verbose_name='数据库实例名称')
    host = CharField(max_length=128, default='', verbose_name='数据库地址')
    port = PositiveSmallIntegerField(default=3306, verbose_name='数据库端口号')
    username = CharField(max_length=32, default='', verbose_name='登录用户名')
    password = CharField(max_length=255, default='', verbose_name='登录密码')

    _password = None

    class Meta:
        db_table = 'metadata_database_config'
        verbose_name = '数据库实例配置'
        verbose_name_plural = verbose_name

        permissions = (
            ('read_database_config', 'Can view database config'),
            ('write_database_config', 'Can write database config'),
        )

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


class SchemaConfig(Base):
    """
    CREATE TABLE metadata_schema_config (
      `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `database_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '数据库实例ID',
      `schema_name` varchar(64) NOT NULL DEFAULT '' COMMENT '数据库名称',
      `is_deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否被删除，0否，1是',
      `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
      `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
      PRIMARY KEY (`id`)
    )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据库配置';
    """

    database = ForeignKey('DatabaseConfig', related_name='database',
                          on_delete=CASCADE, verbose_name='数据库实例ID')
    schema_name = CharField(max_length=64, default='', verbose_name='数据库名称')

    def __str__(self):
        return self.schema_name

    class Meta:
        db_table = 'metadata_schema_config'
        verbose_name = '数据库配置'
        verbose_name_plural = verbose_name

        permissions = (
            ('read_schema_config', 'Can view schema config'),
            ('write_schema_config', 'Can write schema config'),
        )


class TableInfo(Base):
    """
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


    insert into metadata_table_info
    (
        table_schema
        ,table_name
        ,table_comment
        ,table_collation
        ,row_format
        ,create_time
        ,update_time
    )
    select
        b.table_schema
        ,b.table_name
        ,b.table_comment
        ,b.table_collation
        ,b.row_format
        ,b.create_time
        ,b.update_time
    from metadata_schema_config a
    left join `information_schema`.tables b
    on a.schema_name=b.table_schema
    """

    table_schema = CharField(max_length=64, default='', verbose_name='数据库名称')
    table_name = CharField(max_length=64, default='', verbose_name='表名称')
    table_comment = CharField(max_length=255, default='', verbose_name='表备注')
    table_collation = CharField(max_length=32, default='', verbose_name='表字符校验编码集')
    row_format = CharField(max_length=20, default='', verbose_name='表行格式')
    create_time = DateTimeField(null=True, default=None, verbose_name='表创建时间')
    update_time = DateTimeField(null=True, default=None, verbose_name='表更新时间')

    class Meta:
        db_table = 'metadata_table_info'
        verbose_name = '数据表信息'
        verbose_name_plural = verbose_name

        index_together = (
            ('table_name', 'created_time', 'table_schema'),
        )


class ColumnInfo(Base):
    """
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

    insert into metadata_column_info
    (
        table_schema
        ,table_name
        ,column_name
        ,column_type
        ,is_nullable
        ,column_default
        ,extra
        ,column_comment
        ,ordinal_position
        ,character_set_name
        ,collation_name
    )
    select
         b.table_schema
        ,b.table_name
        ,b.column_name
        ,b.column_type
        ,b.is_nullable
        ,b.column_default
        ,b.extra
        ,b.column_comment
        ,b.ordinal_position
        ,b.character_set_name
        ,b.collation_name
    from metadata_schema_config a
    left join `information_schema`.columns b
    on a.schema_name=b.table_schema
    """

    table_schema = CharField(max_length=64, default='', verbose_name='数据库名称')
    table_name = CharField(max_length=64, default='', verbose_name='表名称')
    column_name = CharField(max_length=64, default='', verbose_name='列名称')
    column_type = CharField(max_length=255, default='', verbose_name='列类型')
    is_nullable = CharField(max_length=3, default='', verbose_name='列是否可以为空')
    column_default = CharField(max_length=255, null=True, default=None, verbose_name='列默认值')
    extra = CharField(max_length=30, default='', verbose_name='补充信息')
    column_comment = CharField(max_length=1024, default='', verbose_name='列备注')
    ordinal_position = IntegerField(default=0, verbose_name='列序号')
    character_set_name = CharField(max_length=32, null=True, default=None, verbose_name='列字符集')
    collation_name = CharField(max_length=32, null=True, default=None, verbose_name='列排序字符集')

    class Meta:
        db_table = 'metadata_column_info'
        verbose_name = '字段信息'
        verbose_name_plural = verbose_name

        index_together = (
            ('column_name', 'created_time'),
            ('table_name', 'created_time', 'table_schema'),
        )


class StatisticsInfo(Base):
    """
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

    insert into metadata_statistics_info
    (
        table_schema
        ,table_name
        ,index_name
        ,column_name
        ,seq_in_index
        ,index_type
        ,index_comment
    )
    select
         b.table_schema
        ,b.table_name
        ,b.index_name
        ,b.column_name
        ,b.seq_in_index
        ,b.index_type
        ,b.index_comment
    from metadata_schema_config a
    left join `information_schema`.statistics b
    on a.schema_name=b.table_schema
    """

    table_schema = CharField(max_length=64, default='', verbose_name='数据库名称')
    table_name = CharField(max_length=64, default='', verbose_name='表名称')
    index_name = CharField(max_length=64, default='', verbose_name='索引名称')
    column_name = CharField(max_length=64, default='', verbose_name='列名')
    seq_in_index = IntegerField(default='0', verbose_name='索引列顺序')
    index_type = CharField(max_length=16, default='', verbose_name='索引类型')
    index_comment = CharField(max_length=1024, default='', verbose_name='索引备注')

    class Meta:
        db_table = 'metadata_statistics_info'
        verbose_name = '索引信息'
        verbose_name_plural = verbose_name

        index_together = (
            ('table_name', 'created_time', 'table_schema'),
        )


class Comment(Base):
    """
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
    )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评论'
    """

    user = ForeignKey('auth.User', null=True, related_name='user',
                      on_delete=SET_NULL, verbose_name='用户')
    table_schema = CharField(max_length=64, default='', verbose_name='数据库名称')
    table_name = CharField(max_length=64, default='', verbose_name='数据库名称')
    parent_id = PositiveIntegerField(default='0', verbose_name='被评论的ID')
    content = TextField(null=True, verbose_name='评论内容')

    class Meta:
        db_table = 'metadata_comment'
        verbose_name = '评论'
        verbose_name_plural = verbose_name
