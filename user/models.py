from django.db import models
import django.utils.timezone as timezone


class Base(models.Model):

    class Meta:
        abstract = True

    id = models.AutoField('主键', primary_key=True)
    created_time = models.DateTimeField('创建时间', default=timezone.now)
    updated_time = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)


class Menu(Base):
    """
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

    """
    name = models.CharField(max_length=64, unique=True, verbose_name='菜单名')
    icon_code = models.CharField(max_length=64, default='',
                                 verbose_name='菜单icon编码')
    parent_id = models.PositiveIntegerField(default=0, verbose_name='父菜单')
    order = models.IntegerField(verbose_name='菜单排序, 数值越高排序越靠前')
    menu_url = models.CharField(max_length=128, default='#',
                                verbose_name='菜单路由')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'user_menu'
        verbose_name = '菜单'
        verbose_name_plural = verbose_name

        permissions = (
            ('read_menu', 'Can view menu'),
            ('write_menu', 'Can update menu'),
        )

    @classmethod
    def get_menu_by_request_url(cls, url):
        return dict(menu=Menu.objects.get(menu_url=url))


class GroupMenus(models.Model):
    """
    CREATE TABLE `user_group_menus` (
      `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `group_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '用户组id',
      `menu_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '菜单id',
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户组菜单表';
    """
    group = models.ForeignKey('auth.Group', related_name='group',
                              on_delete=models.CASCADE, verbose_name='组')
    menu = models.ForeignKey('Menu', related_name='menu',
                             on_delete=models.CASCADE,  verbose_name='菜单')

    class Meta:
        db_table = 'user_group_menus'
        verbose_name = '用户组菜单对应'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.group.name + '-' + self.menu.name


class OperationLog(Base):
    """
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

    包括登录记录，打开页面记录，查询记录等
    """
    url = models.CharField(max_length=255, default='/', verbose_name='请求地址')
    method = models.CharField(max_length=12, default='', verbose_name='请求类型')
    headers = models.TextField(verbose_name='请求头')
    body = models.TextField(verbose_name='请求参数')
    user_id = models.PositiveIntegerField(default=0, verbose_name='用户id')
    username = models.CharField(max_length=150, default='', verbose_name='登录名')
    user_agent = models.TextField(verbose_name='客户端类型')
    ip = models.CharField(max_length=15, default='', verbose_name='用户操作ip')

    class Meta:
        db_table = 'user_operation_log'
        verbose_name = '用户操作日志'
        verbose_name_plural = verbose_name

        index_together = (
            ('created_time', 'username'),
        )

        permissions = (
            ('read_log', 'Can view operation log'),
        )
