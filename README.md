## 数据管理后台

数据管理后台主要包括数据字典以及数仓公共维度表。

### 1. 安装启动说明
1. 复制配置文件
    ```
    cp my_common/settings.py.default my_common/settings.py
    ```
2. **检查修改**配置文件，至少包括
    * 数据库配置`DATABASES`，根据配置的数据库 NAME ，需要手动创建数据库，配置的字符集应该选择 utf8mb4
    * 日志目录配置`BASE_LOG_DIR`
    * 缓存配置`CACHES`，如果不适用可以注释掉 CACHES、SESSION_ENGINE、SESSION_CACHE_ALIAS
    * 如果 DEBUG = FALSE，需要配置 STATIC_ROOT 目录
    
3. 需要 Python3.6+ 环境，然后安装依赖包
    ```
    pip3 install -r requirement.txt
    ```
4. 修改 django 部分代码
    ```
    django/db/backends/mysql/base.py 注释掉 35、36 行
    django/db/backends/mysql/operations.py 146 行 decode 改为 encode
    ```
5. 数据初始化，只在初始化时执行一次
    ```
    python3 manage.py makemigrations
    python3 manage.py migrate
    python3 manage.py initdata user
    python3 manage.py initdata metadata
    python3 manage.py initdata monitor
    python3 manage.py initdata common
    ```
6. 创建管理员
    ```
    python3 manage.py createsuperuser
    ```
7. DEBUG = FALSE 时静态资源处理
    ```
    python3 manage.py collectstatic
    ```
8. 本地启动方式
    ```
    python3 manage.py runserver
    ```
9. gunicorn 启动
    ```
    gunicorn my_common.wsgi -b 0.0.0.0:8000
    ```
10. 如果需要定时任务或者异步任务处理，单独启动 celery
    ```
    python3 manage.py celery worker -l info
    python3 manage.py celery beat -A my_common.celery_task -l info
    ```
    
### 2. 项目结构
1. `my_common` 配置目录
2. `static` 静态文件
3. `templates` 页面模板文件
3. `utils` 通用组件模块
4. `user` 用户以及权限相关模块
5. `metedata` 元数据模块
6. `common` 公共维度模块
7. `monitor` 监控模块