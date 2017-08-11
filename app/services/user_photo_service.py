import datetime
from app.models import db
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask, request, redirect, url_for, send_from_directory
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES
from werkzeug import secure_filename
import os
#import model class
from app.models.user_photo import UserPhoto
from app.models.base_model import BaseModel

app = Flask(__name__)
#defaul saving, database saving & domain based url
app.config['POST_USER_PHOTO_DEST'] = 'app/static/images/users/'
app.config['SAVE_USER_PHOTO_DEST'] = 'images/users/'
app.config['GET_USER_PHOTO_DEST'] = 'static/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

class UserPhotoService():

    # Photo URL helper, turn into domain based url

    def urlHelper(self, url):
        return request.url_root  + app.config['GET_USER_PHOTO_DEST'] + url

    # For a given file, return whether it's an allowed type or not
    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']
            
    def get(self):
        userPhotos = BaseModel.as_list(db.session.query(UserPhoto).all())
        for userPhoto in userPhotos:
            userPhoto['url'] = self.urlHelper(userPhoto['url'])
        return userPhotos

    def show(self, user_id):
        userPhoto = db.session.query(UserPhoto).filter_by(user_id=user_id).first().as_dict()
        userPhoto['url'] = self.urlHelper(userPhoto['url'])
        return userPhoto
   
    def create(self, payloads):
        image_data = payloads['image_data']
        user_id = payloads['user_id']
        file = request.files['image_data']
        ext = (file.filename.rsplit('.',1)[1])
        if file and self.allowed_file(file.filename):
            self.model_user_photo = UserPhoto()
            db.session.add(self.model_user_photo)
            try:
                now = datetime.datetime.now()
                filename = str(now.year) +  str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second) + str(now.microsecond) + '.' + ext
                file.save(os.path.join(app.config['POST_USER_PHOTO_DEST'], filename))
                self.model_user_photo.url = app.config['SAVE_USER_PHOTO_DEST'] + filename
                self.model_user_photo.user_id = user_id
                db.session.commit()
                data = self.model_user_photo.as_dict()
                data['url'] = self.urlHelper(self.model_user_photo.url)
                return {
                    'error': False,
                    'data': data
                }
            except SQLAlchemyError as e:
                data = e.orig.args
                return {
                    'error': True,
                    'data': data
			}

    def update(self, payloads):
        image_data = payloads['image_data']
        user_id = payloads['user_id']
        file = request.files['image_data']
        ext = (file.filename.rsplit('.',1)[1])
        if file and self.allowed_file(file.filename):
            try:
                now = datetime.datetime.now()
                filename = str(now.year) +  str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second) + str(now.microsecond) + '.' + ext
                file.save(os.path.join(app.config['POST_USER_PHOTO_DEST'], filename))
                newUrl = app.config['SAVE_USER_PHOTO_DEST'] + filename
                self.model_user_photo = db.session.query(UserPhoto).filter_by(user_id=user_id)
                self.user_photo = db.session.query(UserPhoto).filter_by(user_id=user_id).first()
                os.remove(self.user_photo.url)
                self.model_user_photo.update({
                    'url': newUrl,
                    'updated_at': datetime.datetime.now()
                })
                db.session.commit()
                data = self.model_user_photo.first().as_dict()
                data['url'] = self.urlHelper(newUrl)
                return {
                    'error': False,
                    'data': data
                }
            except SQLAlchemyError as e:
                data = e.orig.args
                return {
                    'error': True,
                    'data': data
                }
    
    def delete(self, user_id):
        self.model_user_photo = db.session.query(UserPhoto).filter_by(user_id=user_id)
        if self.model_user_photo.first() is not None:
            #delete row
            self.model_user_photo.delete()
            db.session.commit()
            return {
                'error': False,
                'data': None
            }
        else:
            data = 'data not found'
            return {
                'error': True,
                'data':data
            }   




