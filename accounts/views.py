from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages, auth
from django.urls import reverse

from accounts.models import Token


def send_login_email(request):
    '''отправить сообщение для входа в систему'''
    email = request.POST['email']
    token = Token.objects.create(email=email)
    url = request.build_absolute_uri(
        reverse('login') + '?token=' + str(token.uid)
    )
    message_body = f'Use this link to log in:\n\n{url}'
    send_mail(
        'Your login link for Superlists',
        message_body,
        'klimrus61@yandex.ru',
        [email],
    )
    messages.success(
        request,
        "Check your mail, we sent the link for you, \
        which you can use for login on site."
    )
    return redirect('/')

def login(request):
    '''Авторизовать пользователя'''
    user = auth.authenticate(request, uid=request.GET.get('token'))
    if user:
        auth.login(request, user)
    return redirect('/')