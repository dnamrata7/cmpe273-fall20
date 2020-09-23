#import flask
from flask import Flask,request,send_file, Response
from markupsafe import escape
from sqlitedict import SqliteDict
import json
import random
import string
import html
import hashlib
import qrcode
import werkzeug

app = Flask(__name__)
#Stats(app)
app.config["DEBUG"] = True
bookmarkDict = SqliteDict('./bookmark_db.sqlite',encode=json.dumps, decode=json.loads, autocommit=True)
statsDict = SqliteDict('./stats_db.sqlite',encode=json.dumps, decode=json.loads, autocommit=True)
cache = SqliteDict('./cache_db.sqlite',encode=json.dumps, decode=json.loads, autocommit=True)

def getId():
    letters_and_digits = string.ascii_lowercase + string.digits
    result = ''.join((random.choice(letters_and_digits) for i in range(6)))
    return result

def without_keys(d, *keys):
     return dict(filter(lambda key_value: key_value[0] not in keys, d.items()))

def getFormattedData(data):
    return json.dumps(data, indent=4).replace(' ', '&nbsp').replace(',\n', ',<br>').replace('\n', '<br>')

@app.route('/api/bookmarks',methods=['POST'])
def addBookmark():
    if request.is_json:
        request_data = request.get_json()
        response_data={}
        url=request_data['url']
        id = hashlib.md5(url.encode()).hexdigest()
        if id in bookmarkDict:
            return Response(getFormattedData({'reason' : 'The given URL already exists in the system.'}), status=400, mimetype='application/json')
            #return " <html><h3>400 Bad Request</h3> <p>{'Reason' : The given URL already existed in the system. }</p></html>",400
        else:
            response_data['id'] = id
            statsDict[id]=0
            request_data['count'] = 0
            bookmarkDict[id] = {**response_data,**request_data}
            return Response(getFormattedData(response_data), status=201, mimetype='application/json')    
    else:
        return "Invalid input data format. Please use JSON ."
    #id=getId()
    #dataSet = {"id":id,"name":name,"url":url,"description":description} 
    #for key, value in bookmarkDict.iteritems():
            #print(key,value)


@app.route('/api/bookmarks/<id>', methods=['GET'])
def getBookmark(id):
    if id in bookmarkDict:
        statsDict[id] += 1
        cache[id]=werkzeug.http.generate_etag(str(statsDict[id]).encode())
        return Response(getFormattedData(bookmarkDict[id]),status=200,mimetype='application/json')
    else:
        return Response(getFormattedData("{'reason' : 'Id not found'}"), status=404, mimetype='application/json')

@app.route('/api/bookmarks/<id>/qrcode', methods=['GET'])
def getQRCode(id):
    if id in bookmarkDict:
        data=bookmarkDict[id]
        qr=qrcode.QRCode(version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4)
        qr.add_data(data['url'])
        qr.make(fit=True)
        url_code = qr.make_image(fill_color="black", back_color="white")
        url_code.save('url_qrcode.png')
        return send_file('url_qrcode.png',attachment_filename='url_qrcode.png')
    else:
        return Response(getFormattedData("{'reason' : 'Id not found'}"), status=404, mimetype='application/json')

@app.route('/api/bookmarks/<id>', methods=['DELETE'])
def deleteBookmark(id):                          
    if id in bookmarkDict:
        bookmarkDict.pop(id)
        statsDict.pop(id)
        cache.pop(id)
    return Response("No content", status=204, mimetype='application/json')

@app.route('/api/bookmarks/<id>/stats', methods=['GET'])
def getBookmarkStats(id):
    if id in bookmarkDict:
        headers = request.headers
        etag = cache.get(id , None)
        if etag == request.if_none_match:
            return Response(status=304)
        elif etag is None:
            new_etag= werkzeug.http.generate_etag(str(statsDict[id]).encode())
            response = Response(getFormattedData(statsDict[id]),status=200,mimetype='application/json')
            response.set_etag(new_etag)
            cache[id] = new_etag
        else:
            response = Response(getFormattedData(statsDict[id]),status=200,mimetype='application/json')
            response.set_etag(etag)
        return response
    else:
        return Response(getFormattedData({'reason' : 'Id not found'}), status=404, mimetype='application/json')

    

app.run()