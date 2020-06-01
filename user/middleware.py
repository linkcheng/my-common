#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from django.http.request import QueryDict
from django.utils.deprecation import MiddlewareMixin

from user.models import OperationLog


class OperationLogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if not ip:
            ip = request.META.get('REMOTE_ADDR', '')
        else:
            ip = ip.split(',')[0]

        kwargs = {
            'url': request.path,
            'method': request.method,
            'headers': request.headers,
            'body': QueryDict(request.body).dict(),
            'user_id': request.user.id or 0,
            'username': request.user.username or '',
            'user_agent': request.META.get('HTTP_USER_AGENT', 'unknown'),
            'ip': ip,
        }
        OperationLog.objects.create(**kwargs)
