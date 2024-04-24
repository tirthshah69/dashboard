from flask import redirect, render_template, flash, request, session, url_for
from base import app
import os
from base.com.service_layer.detection_service import PerformDetection
from base.com.vo.detection_vo import LoginVO, DetectionVO
from base.com.dao.detection_dao import LoginDAO, DetectionDAO
from werkzeug.utils import secure_filename
import bcrypt
import time
import json
from datetime import datetime

login_required_message="Login Required"

def convert_timestamp_to_datetime(timestamp):
    date_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    return str(date_time)

@app.route('/', methods=['GET'])
def load_login_page():
    try:
        return render_template("loginPage.html")
    except Exception as e:
        return render_template('errorPage.html', error=e)
    
    
@app.route('/login', methods=['POST'])
def validate_login():
    try:
        login_username = request.form.get('loginUsername')
        login_password = request.form.get('loginPassword')
        login_dao = LoginDAO()
        login_vo_list = login_dao.get_login_data(
            login_username=login_username)
        if login_vo_list is not None and bcrypt.checkpw(
                login_password.encode(),
                login_vo_list.login_password.encode()):
            session['login_id'] = login_vo_list.login_id
            return redirect('/upload')
        else:
            flash("Invalid Credentials")
            return redirect('/')
    except Exception as e:
        return render_template('errorPage.html', error=e)
    

@app.route('/dashboard')
def load_dashboard_page():
    try:    
        if session.get('login_id', 0) > 0:
            return render_template('dashboardPage.html')
        else:
            flash(login_required_message)
            return redirect('/')

    except Exception as e:
        return render_template('errorPage.html', error=e)
    
        
@app.route('/upload')
def load_upload_page():
    try:    
        if session.get('login_id', 0) > 0:
            return render_template('uploadPage.html')
        else:
            flash(login_required_message)
            return redirect('/')

    except Exception as e:
        return render_template('errorPage.html', error=e)
             
           
@app.route('/upload-file', methods=['POST'])
def upload_file():
    try:
        selected_model = request.form.get('detectionModel')
        uploaded_file = request.files.get('uploadedFile')

        detection_vo = DetectionVO()
        detection_dao = DetectionDAO()

        detection_service = PerformDetection(selected_model)
        infer_filename = secure_filename(uploaded_file.filename)

        input_file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                      infer_filename)
        output_file_path = os.path.join(app.config['OUTPUT_FOLDER'],
                                        infer_filename)
        created_on = int(time.time())
        modified_on = int(time.time())
        uploaded_file.save(input_file_path)

        detection_service_output = None
        file_type = None

        if infer_filename.endswith(('.jpg', '.png', '.jpeg')):
            file_type = 'image'
            detection_service_output \
                = detection_service.image_detection_service(input_file_path,
                                                            output_file_path)
        elif infer_filename.endswith(('.mp4', '.mov', '.avi', 'mkv')):
            file_type = 'video'
            detection_service_output \
                = detection_service.video_detection_service(input_file_path,
                                                            output_file_path)

        else:
            raise TypeError("File type not allowed.")

        detection_datetime = detection_service_output.get('detection_datetime', None)
        if detection_datetime is None:
            detection_datetime = 0
        detection_stats = detection_service_output.get('detection_stats', None)
        detection_login_id = session.get('login_id', None)

        print(detection_stats)

        detection_vo.input_file_path = input_file_path
        detection_vo.output_file_path = output_file_path
        detection_vo.detection_type = selected_model
        detection_vo.detection_datetime = detection_datetime
        detection_vo.detection_stats = json.dumps(dict(detection_stats))
        detection_vo.is_deleted = False
        detection_vo.created_on = created_on
        detection_vo.modified_on = modified_on
        detection_vo.created_by = detection_login_id
        detection_vo.modified_by = detection_login_id

        detection_id = detection_dao.admin_detection_insert(detection_vo)

        return redirect(f'/results?detection_id={detection_id}')
    except Exception as e:
        return render_template('errorPage.html', error=e)

@app.route('/results')
def load_results_page():
    try:
        if session.get('login_id', 0) > 0:
            detection_dao = DetectionDAO()
            detection_id = request.args.get('detection_id', None)
            detection_vo = detection_dao.admin_detection_get(detection_id)
            detection_vo.detection_stats = json.loads(detection_vo.detection_stats)
            return render_template('resultsPage.html',
                                   detection_vo=detection_vo)
    except Exception as e:
        return render_template('errorPage.html', error=e)

    
@app.route('/view')
def load_view_page():
    try:
        if session.get('login_id', 0) > 0:
            detection_dao = DetectionDAO()
            detection_vo_list = detection_dao.admin_detection_view(session.get('login_id'))
            for detection_vo, login_vo in detection_vo_list:
                detection_vo.detection_datetime = convert_timestamp_to_datetime(
                    detection_vo.detection_datetime) if (
                    detection_vo.detection_datetime) != 0 else '-'
                detection_vo.created_on = convert_timestamp_to_datetime(detection_vo.created_on)
                detection_vo.modified_on = convert_timestamp_to_datetime(detection_vo.modified_on)
                detection_vo.detection_stats = json.loads(detection_vo.detection_stats)
            return render_template('viewPage.html', detection_vo_list=
            detection_vo_list)
        else:
            flash(login_required_message)
            return redirect('/')
    except Exception as e:
        return render_template('errorPage.html', error=e)


@app.route('/delete')
def admin_delete_record():
    try:
        if session.get('login_id', 0) > 0:
            detection_dao = DetectionDAO()
            detection_vo = DetectionVO()

            detection_id = request.args.get('detection_id')

            detection_vo_list = detection_dao.admin_detection_get(detection_id)

            detection_vo.detection_id = detection_vo_list.detection_id
            detection_vo.is_deleted = True
            detection_vo.modified_on = int(time.time())
            detection_vo.modified_by = session.get('login_id')
            detection_dao.admin_detection_update(detection_vo)

            return redirect('/view')
        else:
            flash(login_required_message)
            return redirect('/')
    except Exception as e:
        return render_template('errorPage.html', error=e)


@app.route('/view-file')
def load_file_show_page():
    try:
        if session.get('login_id', 0) > 0:
            path = request.args.get('path')
            return render_template('fileShowPage.html', path=path)
        else:
            flash(login_required_message)
            return redirect('/')
    except Exception as e:
        return render_template('errorPage.html', error=e)

@app.route('/about')
def load_about_page():
    try:
        if session.get('login_id', 0) > 0:
            return render_template('aboutPage.html')
        else:
            flash(login_required_message)
            return redirect('/')
    except Exception as e:
        return render_template('errorPage.html', error=e)
           
        
@app.route('/logout')
def logout():
    try:
        session.clear()
        return redirect('/')

    except Exception as e:
        return render_template('errorPage.html', error=e)