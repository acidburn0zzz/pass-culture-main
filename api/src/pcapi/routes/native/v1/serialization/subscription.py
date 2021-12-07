from typing import Optional

from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import school_types
from pcapi.core.users import models as users_models
from pcapi.serialization.utils import to_camel

from . import BaseModel


class NextSubscriptionStepResponse(BaseModel):
    next_subscription_step: Optional[subscription_models.SubscriptionStep]
    maintenance_page_type: Optional[subscription_models.MaintenancePageType]
    allowed_identity_check_methods: list[subscription_models.IdentityCheckMethod]

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class ProfileUpdateRequest(BaseModel):
    activity: users_models.ActivityEnum
    address: Optional[str]
    city: str
    first_name: str
    last_name: str
    postal_code: str
    school_type: Optional[users_models.SchoolTypeEnum]

    class Config:
        alias_generator = to_camel


class SchoolTypeResponseModel(BaseModel):
    id: school_types.SCHOOL_TYPE_ID_ENUM
    label: school_types.SCHOOL_TYPE_LABEL_ENUM

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class ActivityResponseModel(BaseModel):
    id: school_types.ACTIVITY_ID_ENUM
    label: school_types.ACTIVITY_LABEL_ENUM
    associated_school_types_ids: Optional[list[school_types.SCHOOL_TYPE_ID_ENUM]]

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


class SchoolTypesResponse(BaseModel):
    activities: list[ActivityResponseModel]
    school_types: list[SchoolTypeResponseModel]
