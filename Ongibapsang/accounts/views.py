from django import forms
from django.contrib.auth import get_user_model, login
from django.core.validators import RegexValidator
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
# Create your views here.
# 회원가입은 배달원 모듈 구현할 시 고려

from django import forms
from django.core.validators import RegexValidator

#회원가입 (추후 결정되는 로직에 따라 구현)
# def signup(request):
#     if request.method == "POST":


# 토큰 로그인 폼 정의 
class TokenOnlyForm(forms.Form):
    token = forms.CharField(
        max_length=6, min_length=6,
        validators=[RegexValidator(r'^\d{6}$', '6자리 숫자를 입력하세요.')], # 숫자 6자리만 허용
        widget=forms.TextInput(attrs={"placeholder":"6자리 토큰","inputmode":"numeric","autofocus":True}),
        label="토큰",
    )

@require_http_methods(["GET", "POST"]) #다른 메서드는 405 

def login(request):
    next_url = request.GET.get("next") or request.POST.get("next") or "/"  #로그인 성공 후 이동할 주소 결정 
    if request.method == "GET":
        return render(request, "accounts/token_login.html", {"form": TokenOnlyForm(), "next": next_url})

    form = TokenOnlyForm(request.POST)
    if not form.is_valid():
        return render(request, "accounts/token_login.html", {"form": form, "next": next_url})

    token = form.cleaned_data["token"]
    user = User.objects.filter(token=token, is_active=True).first()
    if not user:
        return render(request, "accounts/token_login.html",
                      {"form": form, "next": next_url, "error": "토큰이 올바르지 않습니다."})

    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return redirect(next_url)