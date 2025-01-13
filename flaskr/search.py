from flask import Blueprint,render_template,request,jsonify
from flaskr.models import Student
bp=Blueprint("search",__name__)

@bp.route('/admin-search')
def search_dashboard():
    arg=request.args.get('search','')
    if arg:
        email=Student.query.filter(Student.email.ilike(f"%{arg}%")).all()
    else:
        email=None
    return render_template('search.html',email=email)