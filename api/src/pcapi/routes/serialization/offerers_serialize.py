from datetime import datetime
from typing import Iterable

import sqlalchemy.orm as sqla_orm

from pcapi import settings
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offerers.models import Target
import pcapi.core.offerers.repository as offerers_repository
from pcapi.routes.native.v1.serialization.common_models import AccessibilityComplianceMixin
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization.venues_serialize import DMSApplicationForEAC
from pcapi.serialization.utils import humanize_field
import pcapi.utils.date as date_utils


class GetOffererVenueResponseModel(BaseModel, AccessibilityComplianceMixin):
    adageInscriptionDate: datetime | None
    address: str | None
    bookingEmail: str | None
    city: str | None
    comment: str | None
    departementCode: str | None
    hasMissingReimbursementPoint: bool
    hasCreatedOffer: bool
    hasAdageId: bool
    id: str
    isVirtual: bool
    managingOffererId: str
    name: str
    nonHumanizedId: int
    postalCode: str | None
    publicName: str | None
    siret: str | None
    venueLabelId: str | None
    venueTypeCode: offerers_models.VenueTypeCode
    withdrawalDetails: str | None
    collectiveDmsApplications: list[DMSApplicationForEAC]
    _humanize_id = humanize_field("id")
    _humanize_managing_offerer_id = humanize_field("managingOffererId")
    _humanize_venue_label_id = humanize_field("venueLabelId")

    @classmethod
    def from_orm(
        cls,
        venue: offerers_models.Venue,
        ids_of_venues_with_offers: Iterable[int] = (),
    ) -> "GetOffererVenueResponseModel":
        now = datetime.utcnow()
        venue.hasMissingReimbursementPoint = not (
            any(
                (
                    now > link.timespan.lower and (link.timespan.upper is None or now < link.timespan.upper)
                    for link in venue.reimbursement_point_links
                )
            )
            or venue.hasPendingBankInformationApplication
        )
        venue.hasCreatedOffer = venue.id in ids_of_venues_with_offers
        venue.hasAdageId = bool(venue.adageId)
        return super().from_orm(venue)

    class Config:
        orm_mode = True
        json_encoders = {datetime: date_utils.format_into_utc_date}


class OffererApiKey(BaseModel):
    maxAllowed: int
    prefixes: list[str]


class GetOffererResponseModel(BaseModel):
    address: str | None
    apiKey: OffererApiKey
    bic: str | None
    city: str
    dateCreated: datetime
    dateModifiedAtLastProvider: datetime | None
    demarchesSimplifieesApplicationId: str | None
    fieldsUpdated: list[str]
    hasAvailablePricingPoints: bool
    hasDigitalVenueAtLeastOneOffer: bool
    hasMissingBankInformation: bool
    iban: str | None
    id: str
    idAtProviders: str | None
    isValidated: bool
    isActive: bool
    lastProviderId: str | None
    # see end of `from_orm()`
    managedVenues: list[GetOffererVenueResponseModel] = []
    name: str
    nonHumanizedId: int
    postalCode: str
    # FIXME (dbaty, 2020-11-09): optional until we populate the database (PC-5693)
    siren: str | None

    _humanize_id = humanize_field("id")

    @classmethod
    def from_orm(cls, offerer: offerers_models.Offerer) -> "GetOffererResponseModel":
        offerer.apiKey = {
            "maxAllowed": settings.MAX_API_KEY_PER_OFFERER,
            "prefixes": offerers_repository.get_api_key_prefixes(offerer.id),
        }
        venues = (
            offerers_models.Venue.query.filter_by(managingOffererId=offerer.id)
            .options(sqla_orm.joinedload(offerers_models.Venue.reimbursement_point_links))
            .options(sqla_orm.joinedload(offerers_models.Venue.bankInformation))
            .options(sqla_orm.joinedload(offerers_models.Venue.collectiveDmsApplications))
            .order_by(offerers_models.Venue.common_name)
            .all()
        )

        offerer.hasDigitalVenueAtLeastOneOffer = offerers_repository.has_digital_venue_with_at_least_one_offer(
            offerer.id
        )
        offerer.hasMissingBankInformation = not offerer.demarchesSimplifieesApplicationId and (
            offerers_repository.has_physical_venue_without_draft_or_accepted_bank_information(offerer.id)
            or offerer.hasDigitalVenueAtLeastOneOffer
        )
        offerer.hasAvailablePricingPoints = any(venue.siret for venue in offerer.managedVenues)

        # We would like the response attribute to be called
        # `managedVenues` but we don't want to use the
        # `Offerer.managedVenues` relationship which does not
        # join-load what we want.
        res = super().from_orm(offerer)
        ids_of_venues_with_offers = offerers_repository.get_ids_of_venues_with_offers([offerer.id])

        res.managedVenues = [
            GetOffererVenueResponseModel.from_orm(venue, ids_of_venues_with_offers) for venue in venues
        ]
        return res

    class Config:
        orm_mode = True
        json_encoders = {datetime: date_utils.format_into_utc_date}


class GetOffererNameResponseModel(BaseModel):
    id: str
    nonHumanizedId: int
    name: str

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetOfferersNamesResponseModel(BaseModel):
    offerersNames: list[GetOffererNameResponseModel]

    class Config:
        orm_mode = True


class GetOfferersNamesQueryModel(BaseModel):
    validated: bool | None
    # FIXME (dbaty, 2022-05-04): rename to something clearer, e.g. `include_non_validated_user_offerers`
    validated_for_user: bool | None
    offerer_id: str | None

    class Config:
        extra = "forbid"


class GetEducationalOffererVenueResponseModel(BaseModel, AccessibilityComplianceMixin):
    address: str | None
    city: str | None
    id: str
    isVirtual: bool
    publicName: str | None
    name: str
    postalCode: str | None
    collectiveInterventionArea: list[str] | None
    collectivePhone: str | None
    collectiveEmail: str | None
    collectiveSubCategoryId: str | None
    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetEducationalOffererResponseModel(BaseModel):
    id: str
    name: str
    managedVenues: list[GetEducationalOffererVenueResponseModel]

    _humanize_id = humanize_field("id")

    class Config:
        orm_mode = True


class GetEducationalOfferersResponseModel(BaseModel):
    educationalOfferers: list[GetEducationalOffererResponseModel]

    class Config:
        orm_mode = True


class GetEducationalOfferersQueryModel(BaseModel):
    offerer_id: str | None

    class Config:
        extra = "forbid"


class GenerateOffererApiKeyResponse(BaseModel):
    apiKey: str


class CreateOffererQueryModel(BaseModel):
    address: str | None
    city: str
    latitude: float | None
    longitude: float | None
    name: str
    postalCode: str
    siren: str


class SaveNewOnboardingDataQueryModel(BaseModel):
    # FIXME(fseguin, 2023-03-27): make these attributes not optional when UI is implemented
    createVenueWithoutSiret: bool = False
    publicName: str | None
    siret: str
    target: Target
    venueTypeCode: offerers_models.VenueTypeCode | None
    webPresence: str
    # FIXME(fseguin, 2023-03-27): delete these 2 attributes when pcpro is updated
    name: str | None
    venueType: str | None

    class Config:
        extra = "forbid"
        anystr_strip_whitespace = True


class ReimbursementPointResponseModel(BaseModel):
    venueId: int
    venueName: str
    iban: str


class ReimbursementPointListResponseModel(BaseModel):
    __root__: list[ReimbursementPointResponseModel]


class OffererStatsResponseModel(BaseModel):
    dashboardUrl: str
