from io import BytesIO

from django.http import HttpResponse
from qrcode.constants import ERROR_CORRECT_L
from qrcode.main import QRCode
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from friends.models import DiaryFriend
from qr.models import QrCode
from users.models import User


class QrCodeCreateView(APIView):
    def get(self, request):
        username = request.query_params.get("username")
        if not username:
            return Response({"detail": "username 파라미터가 필요합니다."}, status=400)

        user = get_object_or_404(User, username=username)

        qr_instance, _ = QrCode.objects.get_or_create(
            user=user, defaults={"invite_code": f"{username}_초대코드"}
        )

        try:
            qr = QRCode(
                version=1,
                error_correction=ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_instance.invite_code)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            return HttpResponse(buffer.getvalue(), content_type="image/png")

        except Exception as e:
            print("QR 코드 생성 실패:", str(e))
            return Response(
                {"error": "QR 코드 생성 중 오류 발생", "detail": str(e)}, status=500
            )


def add_friend_by_qr(inviter_invite_code, current_user):
    try:
        qr = QrCode.objects.get(invite_code=inviter_invite_code)
        inviter = qr.user
    except QrCode.DoesNotExist:
        return None, "유효하지 않은 초대코드입니다."

    # 자기 자신에게 친구 요청 불가
    if inviter == current_user:
        return None, "자기 자신에게 친구 요청은 불가합니다."

    # 친구 상태인지 체크
    if DiaryFriend.objects.filter(
        user=current_user, friend_user_id=inviter, status="accepted"
    ).exists():
        return None, "이미 친구입니다."

    diary_friend = DiaryFriend.objects.create(
        user=current_user, friend_user_id=inviter, status="accepted"
    )
    return diary_friend, None
