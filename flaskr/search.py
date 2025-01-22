from flask import Blueprint,render_template,request,jsonify
from flaskr.models import Student
from flaskr.login import permission_required
bp=Blueprint("search",__name__)

@bp.route('/admin-search')
@permission_required('search_dashboard')
def search_dashboard():
    arg=request.args.get('search','')
    if arg:
        email=Student.query.filter(Student.email.ilike(f"%{arg}%")).all()
    else:
        email=None
    return render_template('search.html',email=email)