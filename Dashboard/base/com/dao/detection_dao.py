from base import db
from base.com.vo.detection_vo import LoginVO, DetectionVO

# Query for files data
class LoginDAO:
    def get_login_data(self, login_username: str):
        login_username_data = LoginVO.query.filter_by(
            login_username=login_username).first()
        return login_username_data


# Query for Potholes data   
class DetectionDAO:
    def admin_detection_insert(self, detection_vo: DetectionVO):
        db.session.add(detection_vo)
        db.session.commit()
        db.session.refresh(detection_vo)
        return detection_vo.detection_id

    def admin_detection_view(self, login_id):
        detection_vo_list = db.session.query(
            DetectionVO, LoginVO).filter(
                DetectionVO.created_by == LoginVO.login_id,
                DetectionVO.created_by == login_id,
                DetectionVO.is_deleted == False).all()
        return detection_vo_list

    def admin_detection_get(self, detection_id):
        detection_vo_list = DetectionVO.query.filter_by(
            detection_id=detection_id).first()
        return detection_vo_list

    def admin_detection_update(self, detection_vo):
        db.session.merge(detection_vo)
        db.session.commit()


