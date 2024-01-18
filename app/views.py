from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import time
import random
import requests
from concurrent import futures

CALLBACK_URL = "http://localhost:8000/async"
AUTH_KEY = "secret-async-passports"

executor = futures.ThreadPoolExecutor(max_workers=1)

def get_random_fact(request_refer, passport_refer):
    time.sleep(5)
    return {
        "request_refer": request_refer,
        "passport_refer": passport_refer,
        "is_biometry": bool(random.getrandbits(1)),
    }

def status_callback(task):
    try:
        result = task.result()
        print(result)
    except futures._base.CancelledError:
        return
    
    nurl = str(CALLBACK_URL + "/" + str(result["request_refer"]) + "/" + str(result["passport_refer"]))
    print(nurl)
    answer = {"request_refer": result["request_refer"], 
              "passport_refer": result["passport_refer"], 
              "is_biometry": result["is_biometry"]}
    requests.post(nurl, json=answer, timeout=3)

@api_view(['POST'])
def set_plan(request):
    if "Authorization" not in request.headers or request.headers["Authorization"] != AUTH_KEY:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    if ("request_refer" and "passport_refer") in request.data.keys():   
        request_refer = request.data["request_refer"]    
        passport_refer = request.data["passport_refer"]    

        print(request_refer, passport_refer)

        task = executor.submit(get_random_fact, request_refer, passport_refer)
        task.add_done_callback(status_callback)        
        return Response(status=status.HTTP_200_OK)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)