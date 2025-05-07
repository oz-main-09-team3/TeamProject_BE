from rest_framework.views import APIView


class QrView(APIView):
    def get(self, request):
        data = request.query_params.get("data")
        if not data:
            return Response({"detail": "data 파라미터가 필요합니다."}, status=400)
