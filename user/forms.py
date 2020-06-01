#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from django import forms
from django.forms import fields

from user.models import Menu


class MenuForm(forms.ModelForm):
    name = fields.CharField(required=True)
    icon_code = fields.CharField(required=False)
    parent_id = fields.IntegerField(required=True)
    order = fields.IntegerField(required=True)
    menu_url = fields.CharField()

    class Meta:
        model = Menu
        fields = "__all__"
        exclude = [
            'id',
            'is_deleted',
            'created_time',
            'updated_time',
        ]
