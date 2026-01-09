from flask import Blueprint, send_from_directory, current_app
from flask_login import login_required

media_bp = Blueprint("media", __name__)

@media_bp.route("/uploads/photos/<filename>")
@login_required
def user_photo(filename):
    return send_from_directory(
        current_app.config["UPLOAD_PHOTO_FOLDER"],
        filename
    )
