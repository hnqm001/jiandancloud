import os
from datetime import datetime
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, send_file, send_from_directory
from flask_login import login_required, current_user
from . import cloud
from .. import db
from ..models import Permission, Role, User, Post, Comment, Uploadfile
from ..decorators import admin_required, permission_required
from .forms import SearchForm


@cloud.route('/admin/<username>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMIN)
def admin(username):
    form = SearchForm()
    if form.validate_on_submit():
        name = '%'+form.name.data+'%'
        query = User.query.filter(User.username.like(name))
    else:
        query = User.query
    user = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(User.member_since.desc()).paginate(
        page, per_page=10, error_out=False)
    users = pagination.items
    role = Role.query
    return render_template('admin.html', users=users, role=role, user=user,
                           endpoint='.admin', pagination=pagination,
                           form=form, page=page)


@cloud.route('/admin/<int:id>/delete', methods=['POST'])
@login_required
@permission_required(Permission.ADMIN)
def del_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('用户删除成功')
    return redirect(url_for('.admin', username=current_user.username))


@cloud.route('/disk/<username>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.CLOUD)
def disk(username):
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    share_file = False
    if current_user.is_authenticated:
        share_file = bool(request.cookies.get('share_file', ''))
    if form.validate_on_submit():
        name = '%'+form.name.data+'%'
        query = Uploadfile.query.filter(Uploadfile.filename.like(name))
    else:
        if share_file:
            query = Uploadfile.query.filter_by(fileshare=True)
        else:
            query = User.query.filter_by(
                username=username).first_or_404().files
    user = User.query.filter_by(username=username).first_or_404()
    pagination = query.order_by(Uploadfile.timestamp.desc()).paginate(
        page, per_page=12, error_out=False)
    files = pagination.items
    getFileList()
    return render_template('disk.html', user=user, files=files,
                           share_file=share_file, endpoint='.disk',
                           pagination=pagination, form=form)


@cloud.route('/upload', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.CLOUD)
def upload():
    if request.method == 'POST' and 'file' in request.files:
        f = request.files.get('file')  # 获取文件对象
        filename = f.filename
        f.save(os.path.join(
            current_app.config['UPLOAD_PATH'], f.filename))  # 保存文件
        filepath = os.path.join(current_app.config['UPLOAD_PATH'], f.filename)
        filesize = os.path.getsize(filepath)
        filedb = Uploadfile.query.filter_by(filename=filename).first()
        if filedb is not None and filename == filedb.filename and filepath == filedb.filepath:
            filedb.timestamp = datetime.utcnow()
            filedb.filesize = filesize

            db.session.commit()
        else:
            filetype = os.path.splitext(filepath)[1][1:]
            uploadfile = Uploadfile(filename=filename, filepath=filepath,
                                    filesize=filesize, filetype=filetype,
                                    uploader_id=current_user._get_current_object().id)
            db.session.add(uploadfile)
            db.session.commit()
    return render_template('upload.html')


@cloud.route('/download/<filename>', methods=['GET'])
@login_required
@permission_required(Permission.CLOUD)
def download(filename):
    file = Uploadfile.query.filter_by(filename=filename).first()
    filepath = file.filepath
    return send_file(filepath, as_attachment=True, attachment_filename=filename)


@cloud.route('/image/<path:filename>')
@login_required
@permission_required(Permission.CLOUD)
def get_image(filename):
    return send_from_directory(current_app.config['UPLOAD_PATH'], filename)


@cloud.route('/show/<path:filename>')
@login_required
@permission_required(Permission.CLOUD)
def show(filename):
    filename = filename
    filetype = filename.split('.')[1]
    return render_template('show.html', filename=filename, filetype=filetype)


@cloud.route('/disk/<int:id>/delete')
@login_required
@permission_required(Permission.CLOUD)
def del_file(id):
    file = Uploadfile.query.get_or_404(id)
    path = file.filepath
    db.session.delete(file)
    db.session.commit()
    os.remove(path)
    flash('文件删除成功')
    return redirect(url_for('.disk', username=current_user.username))


@cloud.route('/unshare')
@login_required
@permission_required(Permission.CLOUD)
def unshare():
    resp = make_response(
        redirect(url_for('.disk', username=current_user.username)))
    resp.set_cookie('share_file', '', max_age=30*24*60*60)
    return resp


@cloud.route('/fshare')
@login_required
@permission_required(Permission.CLOUD)
def fshare():
    resp = make_response(
        redirect(url_for('.disk', username=current_user.username)))
    resp.set_cookie('share_file', '1', max_age=30*24*60*60)
    return resp


@cloud.route('/fileshare/enable/<int:id>')
@login_required
@permission_required(Permission.CLOUD)
def share_enable(id):
    file = Uploadfile.query.get_or_404(id)
    file.fileshare = True
    db.session.add(file)
    db.session.commit()
    return redirect(url_for('.disk',
                            username=current_user.username))


@cloud.route('/fileshare/disable/<int:id>')
@login_required
@permission_required(Permission.CLOUD)
def share_disable(id):
    file = Uploadfile.query.get_or_404(id)
    file.fileshare = False
    db.session.add(file)
    db.session.commit()
    return redirect(url_for('.disk',
                            username=current_user.username))


def getFileList():
    path = current_app.config['UPLOAD_PATH']
    query = Uploadfile.query
    for root, dirs, files in os.walk(path):
        for name in files:
            filename = name
            filepath = os.path.join(root, name)
            filesize = os.path.getsize(filepath)
            filetype = os.path.splitext(filepath)[1][1:]
            if query.filter_by(filename=filename, filepath=filepath, filesize=filesize).first() is None:
                temp = query.filter_by(
                    filename=filename, filepath=filepath).first()
                if temp is not None:
                    db.session.delete(temp)
                fileinfo = Uploadfile(filename=filename, filepath=filepath,
                                      filesize=filesize, filetype=filetype,
                                      fileshare=True, uploader_id=1)
                db.session.add(fileinfo)
                db.session.commit()
    return redirect(url_for('.disk', username=current_user.username))
