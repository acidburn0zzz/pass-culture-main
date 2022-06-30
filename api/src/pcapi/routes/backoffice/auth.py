from pcapi.core.auth import api as auth_api
from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from . import serialization


@blueprint.backoffice_blueprint.route("auth/token", methods=["GET"])
@spectree_serialize(
    response_model=serialization.AuthTokenResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
def get_auth_token(query: serialization.AuthTokenQuery) -> serialization.AuthTokenResponseModel:
    try:
        token = auth_api.authenticate_with_permissions(query.token)
    except auth_api.NotAPassCultureTeamAccountError:
        raise ApiErrors({"global": "not a passsCulture team account"})

    return serialization.AuthTokenResponseModel(token=token)
