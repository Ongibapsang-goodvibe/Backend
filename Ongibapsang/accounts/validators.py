from django.core.exceptions import ValidationError

class SixDigitPasswordValidator:
    def validate(self, password, user=None):
        if not (password.isdigit() and len(password) == 6):
            raise ValidationError("비밀번호는 반드시 숫자 6자리여야 합니다.")

    def get_help_text(self):
        return "비밀번호는 반드시 숫자 6자리여야 합니다."