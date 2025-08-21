from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
# from .models import Disease   # 필요하면 별도 등록

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = ("id", "username", "district_name", "display_diseases", "is_active", "is_staff")
    search_fields = ("username", "phone", "district_name")
    ordering = ("id",)

    # 편집 화면(기본 UserAdmin 필드 + 커스텀 필드)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("추가 정보", {"fields": ("phone", "address", "district_name", "district_code", "diseases")}),
    )
    # 추가 화면(비번 2칸은 기본 add_fieldsets에 포함)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("추가 정보", {"fields": ("username", "phone", "address", "district_name", "district_code", "diseases")}),
    )

    # M2M 편집 UX
    filter_horizontal = ("groups", "user_permissions", "diseases")
    # (원하면 autocomplete로)
    # autocomplete_fields = ("diseases",)

    # N+1 방지 + 화면 표시용
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("diseases")

    def display_diseases(self, obj):
        return ", ".join(d.name for d in obj.diseases.all())
    display_diseases.short_description = "질환"