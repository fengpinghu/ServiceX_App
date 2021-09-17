from flask import render_template, request, abort
from flask_sqlalchemy import Pagination

from servicex.decorators import oauth_required
from servicex.models import TransformRequest, TransformationResult


@oauth_required
def transformation_results(id_: str):
    if id_.isnumeric():
        treq = TransformRequest.query.get(id_)
    else:
        treq = TransformRequest.query.filter_by(request_id=id_).one()
    if not treq:
        abort(404)
    page = request.args.get('page', 1, type=int)
    filter_by_values = {}
    if status := request.args.get("status"):
        filter_by_values["transform_status"] = status
    pagination: Pagination = TransformationResult.query\
        .filter_by(request_id=treq.request_id, **filter_by_values)\
        .order_by(TransformationResult.file_id.asc())\
        .paginate(page=page, per_page=100, error_out=False)
    return render_template("transformation_results.html", treq=treq, pagination=pagination)
