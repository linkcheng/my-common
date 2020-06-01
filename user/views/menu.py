import logging
from django.views import View
from django.http.request import QueryDict
from django.forms import model_to_dict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator

from user.models import Menu
from user.forms import MenuForm
from user.utils import render_with_menu
from utils.common import jsonify

logger = logging.getLogger(__name__)


class UserMenu(LoginRequiredMixin, View):
    @method_decorator(permission_required('user.read_menu', raise_exception=True))
    def get(self, request, index=0):
        index = int(index)
        if index:
            menu = Menu.objects.filter(id=index).first()
            msg = {
                'status': 'success',
                'data': model_to_dict(menu, exclude=['created_time', 'updated_time'])
            }
            return jsonify(msg)
        else:
            menu_list = Menu.objects.all().order_by('parent_id', '-order').values()

            paginator = Paginator(menu_list, 15)
            # get 方法获取页数
            page = request.GET.get('page', 1)
            try:  # 获取某页
                menu_list = paginator.page(page)
            except PageNotAnInteger:  # 如果 page 参数不为正整数，显示第一页
                menu_list = paginator.page(1)
            except EmptyPage:  # 如果 page 参数为空页，跳到最后一页
                menu_list = paginator.page(paginator.num_pages)

            context = {'menu_list': menu_list}
            if request.user.has_perm('user.write_menu'):
                context['writable'] = '1'

            return render_with_menu(request, 'menu.html', context)

    @method_decorator(permission_required('user.write_menu', raise_exception=True))
    def post(self, request):
        menu = MenuForm(request.POST)

        if menu.is_valid():
            menu.save()
            msg = {'status': 'success'}
        else:
            msg = {
                'status': 'failure',
                'message': '输入格式错误',
            }
        return jsonify(msg)

    @method_decorator(permission_required('user.write_menu', raise_exception=True))
    def put(self, request, index):
        index = int(index)
        data = QueryDict(request.body)

        try:
            Menu.objects.filter(id=index).update(
                name=data.get('name'),
                icon_code=data.get('icon_code'),
                parent_id=int(data.get('parent_id')),
                order=int(data.get('order')),
                menu_url=data.get('menu_url'),
                is_deleted=int(data.get('is_deleted')),
            )
        except Exception as e:
            logger.error(str(e))
            msg = {'status': 'failure', 'message': str(e)}
        else:
            msg = {'status': 'success'}

        return jsonify(msg)

    @method_decorator(permission_required('user.write_menu', raise_exception=True))
    def delete(self, request):
        data = QueryDict(request.body)
        mid = data.get('id')
        try:
            Menu.objects.filter(id=mid).update(is_deleted=True)
        except ValueError as e:
            logger.error(str(e))
            msg = {'status': 'failure', 'message': str(e)}
        else:
            msg = {'status': 'success'}
        return jsonify(msg)
