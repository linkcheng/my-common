import logging
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.views import View

from utils.encryptor import des_encryptor
from utils.common import jsonify, Paginator
from user.utils import render_with_menu, is_already_login
from user.models import OperationLog
from my_common.settings import DES_KEY

logger = logging.getLogger(__name__)


def user_logout(request):
    """ 退出登陆
    :param request:
    :return:
    """
    logout(request)
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        msg = {'status': 'success'}
        return jsonify(msg)


class UserLogin(View):
    def get(self, request):
        """ 这个函数的作用是用来做登陆页面
        :param request:
        :return:
        """
        return render(request, 'login.html', {'key': DES_KEY})

    def post(self, request):
        username = request.POST.get('username')
        pwd = request.POST.get('password')
        password = des_encryptor.decrypt(pwd)

        user = authenticate(username=username, password=password)
        if user is None:
            msg = {
                'status': 'failure',
                'message': '用户名或密码错误',
            }
        elif not user.is_active:
            msg = {
                'status': 'failure',
                'message': '用户未激活',
            }
        elif is_already_login(user):
            msg = {
                'status': 'failure',
                'message': '用户已经在他设备登陆',
            }
        else:
            login(request, user)
            msg = {'status': 'success'}
        return jsonify(msg)


@login_required(login_url='/user/login/')
def show_dashboard(request):
    return render_with_menu(request, 'dashboard.html')


class UserInfo(LoginRequiredMixin, View):
    def get(self, request):
        return render_with_menu(request, 'user.html', {'key': DES_KEY})

    def post(self, request):
        uid = request.POST.get('uid')
        email = request.POST.get('email')

        try:
            user = User.objects.get(id=uid)
            user.email = email
            user.save()
        except Exception as e:
            logger.error(str(e))
            msg = {'status': 'failure', 'message': str(e)}
        else:
            msg = {'status': 'success'}

        return jsonify(msg)


class UserPwd(LoginRequiredMixin, View):
    def get(self, request):
        msg = {'status': 'failure', 'message': 'This method not support GET'}
        return jsonify(msg)

    def post(self, request):
        uid = request.POST.get('uid')
        orig_pwd = request.POST.get('orig_pwd')
        new_pwd1 = request.POST.get('new_pwd1')
        new_pwd2 = request.POST.get('new_pwd2')

        orig_password = des_encryptor.decrypt(orig_pwd)
        new_password1 = des_encryptor.decrypt(new_pwd1)
        new_password2 = des_encryptor.decrypt(new_pwd2)

        if new_password1 != new_password2:
            msg = {
                'status': 'failure',
                'message': '两次输入密码不一致',
            }
            return jsonify(msg)

        user = User.objects.get(id=uid)
        logger.info(orig_password)
        if user.check_password(orig_password):
            user.set_password(new_password1)
            user.save()
            msg = {'status': 'success'}
        else:
            msg = {
                'status': 'failure',
                'message': '原密码输入错误',
            }

        return jsonify(msg)


@permission_required('user.read_log', raise_exception=True)
@login_required(login_url='/user/login/')
def user_operation_log(request, index=0):
    index = int(index)
    if index:
        menu = OperationLog.objects.filter(id=index).first()
        msg = {
            'status': 'success',
            'data': model_to_dict(menu, exclude=['created_time', 'updated_time'])
        }
        return jsonify(msg)
    else:
        log_size = OperationLog.objects.all().order_by('-created_time').count()
        cur_page = request.GET.get('page', 1)
        paginator = Paginator(log_size, cur_page)
        table_name = OperationLog._meta.db_table

        sql = f"""
            select
                *
            from {table_name} a,
            (
                select id 
                from {table_name}
                order by id desc
                limit {paginator.limit} offset {paginator.offset}
            ) b
            where a.id=b.id
            order by a.id desc
            ;
        """  # No QA
        log_list = OperationLog.objects.raw(sql)

        context = {
            'log_list': log_list,
            'paginator': paginator,
        }
        return render_with_menu(request, 'log.html', context)
