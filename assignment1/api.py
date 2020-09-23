
from flask import Flask,request,send_file, Response
from sqlitedict import SqliteDict
import json
import random
import string
import html
import hashlib
import qrcode
import werkzeug

app = Flask(__name__)
app.config["DEBUG"] = True
bookmarkDict = SqliteDict('./bookmark_db.sqlite',encode=json.dumps, decode=json.loads, autocommit=True)


def without_keys(d, *keys):
     return dict(filter(lambda key_value: key_value[0] not in keys, d.items()))

def getFormattedData(data):
    return json.dumps(data, indent=4)

def saveEtagToDB(id):
    tempDict = bookmarkDict[id]
    tempDict['etag']=werkzeug.http.generate_etag(str(bookmarkDict[id]).encode())
    bookmarkDict[id] = tempDict
    bookmarkDict.commit()

def saveCountToDB(id):
    tempDict = bookmarkDict[id]
    current_count = tempDict['count']
    current_count += 1
    tempDict['count'] = current_count
    bookmarkDict[id] = tempDict
    bookmarkDict.commit()


@app.route('/api/bookmarks',methods=['POST'])
def addBookmark():
    if request.is_json:
        request_data = request.get_json()
        response_data={}
        url=request_data['url']
        id = hashlib.md5(url.encode()).hexdigest()
        if id in bookmarkDict:
            return Response(getFormattedData({'reason' : 'The given URL already exists in the system.'}), status=400, mimetype='application/json')
        else:
            response_data['id'] = id
            request_data['count'] = 0
            request_data['etag'] = None
            bookmarkDict[id] = {**response_data,**request_data}
            return Response(getFormattedData(response_data), status=201, mimetype='application/json')    
    else:
        return "Invalid input data format. Please use JSON ."


@app.route('/api/bookmarks/<id>', methods=['GET'])
def getBookmark(id):
    if id in bookmarkDict:
        saveCountToDB(id)
        if bookmarkDict[id]['etag'] is not None:
            saveEtagToDB(id)
        return Response(getFormattedData(without_keys(bookmarkDict[id],'count','etag')),status=200,mimetype='application/json')
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
    return Response("No content", status=204, mimetype='application/json')

@app.route('/api/bookmarks/<id>/stats', methods=['GET'])
def getBookmarkStats(id):
    if id in bookmarkDict:
        headers = request.headers
        etag = bookmarkDict[id]['etag']
        if etag in request.if_none_match:
            return Response(status=304)
        elif etag is None:
            saveEtagToDB(id)
            new_etag = bookmarkDict[id]['etag']
            response = Response(getFormattedData(bookmarkDict[id]['count']),status=200,mimetype='application/json')
            response.set_etag(new_etag)
        else:
            response = Response(getFormattedData(bookmarkDict[id]['count']),status=200,mimetype='application/json')
            response.set_etag(etag)
        return response
    else:
        return Response(getFormattedData({'reason' : 'Id not found'}), status=404, mimetype='application/json')

    

app.run()
