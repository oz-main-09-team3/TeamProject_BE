import qrcode # QR 코드를 만들어주는 파이썬 라이브러리
from io import BytesIO # 이미지를 메모리에 임시로 저장하는 가상의 파일 객체
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView


class QrCodeView(APIView):
    def get(self, request):
        data = request.query_params.get("data") # 예) /api/qrcode/?data=hello123 -> data="hello123"
        if not data: # data 부분이 없으면 오류메시지와 400 Bad Request 응답을 보냄
            return Response({"detail": "data 파라미터가 필요합니다."}, status=400)
        # qrcode.make(): 문자열을 QR 코드 이미지로 자동 변환 해줌 예) "hello123" -> 🟩⬜⬜🟩⬜⬜⬜⬜ 이런 QR 이미지 생성됨
        qr = qrcode.make(data)
        buffer = BytesIO() # 이미지 파일을 메모리(RAM) 상의 가상 파일에 저장하기 위한 준(하드디스크에 저장하지 않고 응답 직전에 메모리에 잠깐 저장)
        qr.save(buffer, format="PNG") # QR 이미지를 PNG 형식으로 buffer에 저장
        buffer.seek(0) # buffer의 파일 커서를 맨 앞으로 이동 -> 이미지 데이터를 읽을 준비를 한다
        # 메모리에 저장된 QR 이미지 데이터를 꺼내서 바로 응답으로 보냄
        # 응답의 Content-Type을 image/png로 설정했기 때문에 브라우저는 이미지를 바로 보여줌
        return HttpResponse(buffer.getvalue(), content_type="image/png")


