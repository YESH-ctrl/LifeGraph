import urllib.request, json
q='Need rice, atta and oil for the entire month'
req=urllib.request.Request('http://127.0.0.1:8000/agents/mission-detection', data=json.dumps({'text': q}).encode('utf-8'), headers={'Content-Type': 'application/json'})
try: 
    res=urllib.request.urlopen(req)
    print(res.read()) 
except Exception as e: 
    print(e.read())
