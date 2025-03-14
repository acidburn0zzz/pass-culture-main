# pylint: disable=redefined-outer-name
import datetime
import json

from flask import url_for
import pytest

from pcapi.core.auth.api import generate_token
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions.models import Permissions
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus

from .fixtures import *  # pylint: disable=wildcard-import, unused-wildcard-import


pytestmark = pytest.mark.usefixtures("db_session")


class GetOffererUsersTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_offerer_users_returns_list(self, client):
        # given
        offerer1 = offerers_factories.OffererFactory()
        uo1 = offerers_factories.UserOffererFactory(
            offerer=offerer1, user=users_factories.ProFactory(firstName=None, lastName=None)
        )
        uo2 = offerers_factories.UserOffererFactory(
            offerer=offerer1, user=users_factories.ProFactory(firstName="Jean", lastName="Bon")
        )
        uo3 = offerers_factories.NotValidatedUserOffererFactory(offerer=offerer1, user=users_factories.ProFactory())

        offerer2 = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer2, user=users_factories.ProFactory())

        auth_token = generate_token(users_factories.UserFactory(), [Permissions.READ_PRO_ENTITY])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for("backoffice_blueprint.get_offerer_users", offerer_id=offerer1.id)
            )

        # then
        assert response.status_code == 200
        assert response.json["data"] == [
            {
                "id": uo1.user.id,
                "firstName": None,
                "lastName": None,
                "email": uo1.user.email,
                "phoneNumber": uo1.user.phoneNumber,
                "user_offerer_id": uo1.id,
                "validationStatus": "VALIDATED",
            },
            {
                "id": uo2.user.id,
                "firstName": "Jean",
                "lastName": "Bon",
                "email": uo2.user.email,
                "phoneNumber": uo2.user.phoneNumber,
                "user_offerer_id": uo2.id,
                "validationStatus": "VALIDATED",
            },
            {
                "id": uo3.user.id,
                "firstName": uo3.user.firstName,
                "lastName": uo3.user.lastName,
                "email": uo3.user.email,
                "phoneNumber": uo3.user.phoneNumber,
                "user_offerer_id": uo3.id,
                "validationStatus": "NEW",
            },
        ]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_offerer_users_returns_empty_if_offerer_is_not_found(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_users", offerer_id=42)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == []

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_users_without_permission(self, client):
        # given
        offerer1 = offerers_factories.OffererFactory()
        auth_token = generate_token(
            users_factories.UserFactory(), [perm for perm in Permissions if perm != Permissions.READ_PRO_ENTITY]
        )

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_users", offerer_id=offerer1.id)
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_users_as_anonymous(self, client):
        # given
        offerer1 = offerers_factories.OffererFactory()

        # when
        response = client.get(url_for("backoffice_blueprint.get_offerer_users", offerer_id=offerer1.id))

        # then
        assert response.status_code == 403


class GetOffererBasicInfoTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_detail_payload_structure(
        self,
        client,
        offerer,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for("backoffice_blueprint.get_offerer_basic_info", offerer_id=offerer.id)
            )

        # then
        assert response.status_code == 200
        assert "data" in response.json
        payload = response.json["data"]
        assert "id" in payload
        assert "name" in payload
        assert "validationStatus" in payload
        assert "isActive" in payload
        assert "siren" in payload
        assert "region" in payload
        assert "bankInformationStatus" in payload
        assert "ko" in payload["bankInformationStatus"]
        assert "ok" in payload["bankInformationStatus"]
        assert "isCollectiveEligible" in payload

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_detail_basic_info(self, client, offerer):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_basic_info", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        payload = response.json["data"]
        assert payload["id"] == offerer.id
        assert payload["name"] == offerer.name
        assert payload["validationStatus"] == ValidationStatus.VALIDATED.value
        assert payload["isActive"] == offerer.isActive
        assert payload["siren"] == offerer.siren
        assert payload["region"] == "Occitanie"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_detail_contains_venue_bank_information_stats(
        self,
        client,
        offerer,
        venue_with_accepted_self_reimbursement_point,
        venue_with_accepted_reimbursement_point,
        venue_with_expired_reimbursement_point,
        venue_with_rejected_bank_info,
        random_venue,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_basic_info", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        bank_info_stats = response.json["data"]["bankInformationStatus"]
        assert bank_info_stats["ko"] == 2
        assert bank_info_stats["ok"] == 2

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_with_educational_venue_is_collective_eligible(
        self,
        client,
        offerer,
        venue_with_educational_status,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_basic_info", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"]["isCollectiveEligible"] is True

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_with_no_educational_venue_is_not_collective_eligible(
        self,
        client,
        offerer,
        venue_with_accepted_bank_info,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_basic_info", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"]["isCollectiveEligible"] is False

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_returns_404_if_offerer_is_not_found(self, client):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_basic_info", offerer_id=42)
        )

        # then
        assert response.status_code == 404

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [perm for perm in Permissions if perm != Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_basic_info", offerer_id=42)
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_as_anonymous(self, client, offerer):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_basic_info", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 403


class GetOffererTotalRevenueTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_total_revenue(
        self,
        client,
        offerer,
        individual_offerer_bookings,
        collective_offerer_booking,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for("backoffice_blueprint.get_offerer_total_revenue", offerer_id=offerer.id)
            )

        # then
        assert response.status_code == 200
        assert response.json["data"] == 1694.0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_total_revenue_individual_bookings_only(
        self,
        client,
        offerer,
        individual_offerer_bookings,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_total_revenue", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == 30.0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_total_revenue_collective_bookings_only(
        self,
        client,
        offerer,
        collective_offerer_booking,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_total_revenue", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == 1664.0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_total_revenue_no_booking(
        self,
        client,
        offerer,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_total_revenue", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_returns_0_if_offerer_is_not_found(self, client):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_total_revenue", offerer_id=42)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [perm for perm in Permissions if perm != Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_total_revenue", offerer_id=42)
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_as_anonymous(self, client, offerer):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_total_revenue", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 403


class GetOffererOffersStatsTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_offers_stats(
        self,
        client,
        offerer,
        offerer_active_individual_offers,
        offerer_inactive_individual_offers,
        offerer_active_collective_offers,
        offerer_inactive_collective_offers,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for("backoffice_blueprint.get_offerer_offers_stats", offerer_id=offerer.id)
            )

        # then
        assert response.status_code == 200
        offer_stats = response.json["data"]
        assert offer_stats["active"]["individual"] == 3
        assert offer_stats["active"]["collective"] == 5
        assert offer_stats["inactive"]["individual"] == 4
        assert offer_stats["inactive"]["collective"] == 6

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_offers_stats_active_only(
        self,
        client,
        offerer,
        offerer_active_individual_offers,
        offerer_active_collective_offers,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_offers_stats", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        offer_stats = response.json["data"]
        assert offer_stats["active"]["individual"] == 3
        assert offer_stats["active"]["collective"] == 5
        assert offer_stats["inactive"]["individual"] == 0
        assert offer_stats["inactive"]["collective"] == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_offers_stats_inactive_only(
        self,
        client,
        offerer,
        offerer_inactive_individual_offers,
        offerer_inactive_collective_offers,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_offers_stats", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        offer_stats = response.json["data"]
        assert offer_stats["active"]["individual"] == 0
        assert offer_stats["active"]["collective"] == 0
        assert offer_stats["inactive"]["individual"] == 4
        assert offer_stats["inactive"]["collective"] == 6

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_offers_stats_0_if_no_offer(
        self,
        client,
        offerer,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_offers_stats", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        offer_stats = response.json["data"]
        assert offer_stats["active"]["individual"] == 0
        assert offer_stats["active"]["collective"] == 0
        assert offer_stats["inactive"]["individual"] == 0
        assert offer_stats["inactive"]["collective"] == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_offers_stats_0_if_offerer_not_found(
        self,
        client,
    ):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_offers_stats", offerer_id=42)
        )

        # then
        assert response.status_code == 200
        offer_stats = response.json["data"]
        assert offer_stats["active"]["individual"] == 0
        assert offer_stats["active"]["collective"] == 0
        assert offer_stats["inactive"]["individual"] == 0
        assert offer_stats["inactive"]["collective"] == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_offers_stats_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [perm for perm in Permissions if perm != Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_offers_stats", offerer_id=42)
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_offers_stats_as_anonymous(self, client, offerer):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_offers_stats", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 403


class GetOffererHistoryTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_offerer_history(self, client):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])
        user_offerer = offerers_factories.UserOffererFactory()
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 3, 13, 1),
            actionType=history_models.ActionType.OFFERER_NEW,
            authorUser=user_offerer.user,
            user=user_offerer.user,
            offerer=user_offerer.offerer,
            comment=None,
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 4, 14, 2),
            actionType=history_models.ActionType.OFFERER_PENDING,
            authorUser=admin,
            user=user_offerer.user,
            offerer=user_offerer.offerer,
            comment="Documents complémentaires demandés",
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 5, 15, 3),
            actionType=history_models.ActionType.COMMENT,
            authorUser=admin,
            user=user_offerer.user,
            offerer=user_offerer.offerer,
            comment="Documents reçus",
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 6, 16, 4),
            actionType=history_models.ActionType.OFFERER_VALIDATED,
            authorUser=admin,
            user=user_offerer.user,
            offerer=user_offerer.offerer,
            comment=None,
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 6, 17, 5),
            actionType=history_models.ActionType.COMMENT,
            authorUser=admin,
            user=user_offerer.user,
            offerer=offerers_factories.UserOffererFactory(user=user_offerer.user).offerer,
            comment="Commentaire sur une autre structure",
        )

        offerer_id = user_offerer.offerer.id

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for("backoffice_blueprint.get_offerer_history", offerer_id=offerer_id)
            )

        # then
        assert response.status_code == 200
        assert response.json["data"] == [
            {
                "type": "Structure validée",
                "date": "2022-10-06T16:04:00Z",
                "authorId": admin.id,
                "authorName": admin.publicName,
                "comment": None,
                "accountId": user_offerer.user.id,
                "accountName": user_offerer.user.publicName,
            },
            {
                "type": "Commentaire interne",
                "date": "2022-10-05T15:03:00Z",
                "authorId": admin.id,
                "authorName": admin.publicName,
                "comment": "Documents reçus",
                "accountId": user_offerer.user.id,
                "accountName": user_offerer.user.publicName,
            },
            {
                "type": "Structure mise en attente",
                "date": "2022-10-04T14:02:00Z",
                "authorId": admin.id,
                "authorName": admin.publicName,
                "comment": "Documents complémentaires demandés",
                "accountId": user_offerer.user.id,
                "accountName": user_offerer.user.publicName,
            },
            {
                "type": "Nouvelle structure",
                "date": "2022-10-03T13:01:00Z",
                "authorId": user_offerer.user.id,
                "authorName": user_offerer.user.publicName,
                "comment": None,
                "accountId": user_offerer.user.id,
                "accountName": user_offerer.user.publicName,
            },
        ]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_offerer_history_empty_when_no_action(self, client, offerer):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 6, 12),
            actionType=history_models.ActionType.COMMENT,
            authorUser=admin,
            offerer=offerers_factories.OffererFactory(),
            comment="Commentaire sur une autre structure",
        )

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_history", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == []

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_offerer_history_empty_when_offerer_not_found(self, client, offerer):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_history", offerer_id=offerer.id + 100)
        )

        # then
        assert response.status_code == 200
        assert response.json["data"] == []

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_history_without_permission(self, client, offerer):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [perm for perm in Permissions if perm != Permissions.READ_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.get_offerer_history", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_history_as_anonymous(self, client, offerer):
        # given

        # when
        response = client.get(url_for("backoffice_blueprint.get_offerer_history", offerer_id=offerer.id))

        # then
        assert response.status_code == 403


class ValidateOffererTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_validate_offerer(self, client):
        # given
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.validate_offerer", offerer_id=user_offerer.offerer.id)
        )

        # then
        assert response.status_code == 204
        db.session.refresh(user_offerer)
        assert user_offerer.offerer.isValidated
        assert user_offerer.user.has_pro_role

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.OFFERER_VALIDATED
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_validate_offerer_returns_404_if_offerer_is_not_found(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.validate_offerer", offerer_id=42)
        )

        # then
        assert response.status_code == 404
        assert response.json["offerer_id"] == "La structure n'existe pas"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_validate_offerer_already_validated(self, client):
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.validate_offerer", offerer_id=user_offerer.offerer.id)
        )

        # then
        assert response.status_code == 400
        assert response.json["offerer_id"] == "La structure est déjà validée"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_validate_offerer_without_permission(self, client):
        # given
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()
        auth_token = generate_token(
            users_factories.UserFactory(), [perm for perm in Permissions if perm != Permissions.VALIDATE_OFFERER]
        )

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.validate_offerer", offerer_id=user_offerer.offerer.id)
        )

        # then
        assert response.status_code == 403
        db.session.refresh(user_offerer)
        assert not user_offerer.offerer.isValidated
        assert not user_offerer.user.has_pro_role
        assert history_models.ActionHistory.query.count() == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_validate_offerer_as_anonymous(self, client):
        # given
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        # when
        response = client.post(url_for("backoffice_blueprint.validate_offerer", offerer_id=user_offerer.offerer.id))

        # then
        assert response.status_code == 403
        db.session.refresh(user_offerer)
        assert not user_offerer.offerer.isValidated
        assert not user_offerer.user.has_pro_role
        assert history_models.ActionHistory.query.count() == 0


class RejectOffererTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_reject_offerer(self, client):
        # given
        user = users_factories.UserFactory()
        offerer = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)  # deleted when rejected
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.reject_offerer", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 204
        db.session.refresh(user)
        db.session.refresh(offerer)
        assert not offerer.isValidated
        assert offerer.isRejected
        assert not user.has_pro_role

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.OFFERER_REJECTED
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_reject_offerer_returns_404_if_offerer_is_not_found(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.reject_offerer", offerer_id=42)
        )

        # then
        assert response.status_code == 404
        assert response.json["offerer_id"] == "La structure n'existe pas"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_reject_offerer_already_rejected(self, client):
        # given
        offerer = offerers_factories.OffererFactory(validationStatus=ValidationStatus.REJECTED)
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.reject_offerer", offerer_id=offerer.id)
        )

        # then
        assert response.status_code == 400
        assert response.json["offerer_id"] == "La structure est déjà rejetée"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_reject_offerer_without_permission(self, client):
        # given
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()
        auth_token = generate_token(
            users_factories.UserFactory(), [perm for perm in Permissions if perm != Permissions.VALIDATE_OFFERER]
        )

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.reject_offerer", offerer_id=user_offerer.offerer.id)
        )

        # then
        assert response.status_code == 403
        db.session.refresh(user_offerer)
        assert not user_offerer.offerer.isValidated
        assert not user_offerer.offerer.isRejected
        assert not user_offerer.user.has_pro_role
        assert history_models.ActionHistory.query.count() == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_reject_offerer_as_anonymous(self, client):
        # given
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        # when
        response = client.post(url_for("backoffice_blueprint.reject_offerer", offerer_id=user_offerer.offerer.id))

        # then
        assert response.status_code == 403
        db.session.refresh(user_offerer)
        assert not user_offerer.offerer.isValidated
        assert not user_offerer.offerer.isRejected
        assert not user_offerer.user.has_pro_role
        assert history_models.ActionHistory.query.count() == 0


class SetOffererPendingTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_set_offerer_pending(self, client):
        # given
        offerer = offerers_factories.NotValidatedOffererFactory()
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.set_offerer_pending", offerer_id=offerer.id),
            json={"comment": "En attente de documents"},
        )

        # then
        assert response.status_code == 204
        db.session.refresh(offerer)
        assert not offerer.isValidated
        assert offerer.validationStatus == ValidationStatus.PENDING
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.OFFERER_PENDING
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId is None
        assert action.offererId == offerer.id
        assert action.venueId is None
        assert action.comment == "En attente de documents"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_set_offerer_pending_without_permission(self, client):
        # given
        offerer = offerers_factories.NotValidatedOffererFactory()
        auth_token = generate_token(
            users_factories.UserFactory(), [perm for perm in Permissions if perm != Permissions.VALIDATE_OFFERER]
        )

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.set_offerer_pending", offerer_id=offerer.id), json={"comment": "Test"}
        )

        # then
        assert response.status_code == 403
        assert offerer.validationStatus == ValidationStatus.NEW
        assert history_models.ActionHistory.query.count() == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_set_offerer_pending_as_anonymous(self, client):
        # given
        offerer = offerers_factories.NotValidatedOffererFactory()

        # when
        response = client.post(
            url_for("backoffice_blueprint.set_offerer_pending", offerer_id=offerer.id), json={"comment": "Test"}
        )

        # then
        assert response.status_code == 403
        assert offerer.validationStatus == ValidationStatus.NEW
        assert history_models.ActionHistory.query.count() == 0


class CommentOffererTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_comment_offerer(self, client):
        # given
        offerer = offerers_factories.NotValidatedOffererFactory()
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.comment_offerer", offerer_id=offerer.id),
            json={"comment": "Code APE non éligible"},
        )

        # then
        assert response.status_code == 204
        db.session.refresh(offerer)
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.COMMENT
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId is None
        assert action.offererId == offerer.id
        assert action.venueId is None
        assert action.comment == "Code APE non éligible"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_comment_offerer_without_permission(self, client):
        # given
        offerer = offerers_factories.NotValidatedOffererFactory()
        auth_token = generate_token(
            users_factories.UserFactory(), [perm for perm in Permissions if perm != Permissions.VALIDATE_OFFERER]
        )

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.comment_offerer", offerer_id=offerer.id),
            json={"comment": "Test"},
        )

        # then
        assert response.status_code == 403
        assert history_models.ActionHistory.query.count() == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_comment_offerer_as_anonymous(self, client):
        # given
        offerer = offerers_factories.NotValidatedOffererFactory()

        # when
        response = client.post(
            url_for("backoffice_blueprint.comment_offerer", offerer_id=offerer.id), json={"comment": "Test"}
        )

        # then
        assert response.status_code == 403
        assert history_models.ActionHistory.query.count() == 0


class GetOfferersTagsTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_offerers_tags_list(self, client):
        # given
        tag1 = offerers_factories.OffererTagFactory(name="test-top-acteur", label="Top acteur")
        tag2 = offerers_factories.OffererTagFactory(name="test-type-ei", label="Entreprise individuelle")
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.MANAGE_PRO_ENTITY])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for("backoffice_blueprint.get_offerers_tags_list")
            )

        # then
        assert response.status_code == 200
        assert response.json["data"] == [
            {
                "id": tag2.id,
                "name": tag2.name,
                "label": tag2.label,
            },
            {
                "id": tag1.id,
                "name": tag1.name,
                "label": tag1.label,
            },
        ]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerers_tags_list_without_permission(self, client):
        # given
        offerers_factories.OffererTagFactory()
        auth_token = generate_token(
            users_factories.UserFactory(), [perm for perm in Permissions if perm != Permissions.MANAGE_PRO_ENTITY]
        )

        # when
        response = client.with_explicit_token(auth_token).get(url_for("backoffice_blueprint.get_offerers_tags_list"))

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerers_tags_list_as_anonymous(self, client):
        # given
        offerers_factories.OffererTagFactory()

        # when
        response = client.get(url_for("backoffice_blueprint.get_offerers_tags_list"))

        # then
        assert response.status_code == 403


class AddOffererTagTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_add_tag_to_offerer(self, client):
        # given
        # create 2 offerers and 2 tags to ensure that only one tag is added to only one offerer
        offerer = offerers_factories.OffererFactory()
        offerers_factories.OffererFactory()
        tag = offerers_factories.OffererTagFactory(name="test-top-acteur", label="Top acteur")
        offerers_factories.OffererTagFactory(name="test-type-ei", label="Entreprise individuelle")
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.MANAGE_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.add_tag_to_offerer", offerer_id=offerer.id, tag_name=tag.name)
        )

        # then
        assert response.status_code == 204
        offerer_tag_mapping = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_tag_mapping) == 1
        assert offerer_tag_mapping[0].offererId == offerer.id
        assert offerer_tag_mapping[0].tagId == tag.id

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_add_tag_to_offerer_twice(self, client):
        # given
        offerer = offerers_factories.OffererFactory()
        tag = offerers_factories.OffererTagFactory(name="test-tag", label="Test Tag")
        offerers_factories.OffererTagMappingFactory(offererId=offerer.id, tagId=tag.id)
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.MANAGE_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.add_tag_to_offerer", offerer_id=offerer.id, tag_name=tag.name)
        )

        # then
        assert response.status_code == 400
        assert response.json["global"] == ["Une entrée avec cet identifiant existe déjà dans notre base de données"]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_add_tag_to_offerer_without_permission(self, client):
        # given
        offerer = offerers_factories.OffererFactory()
        tag = offerers_factories.OffererTagFactory(name="test-tag", label="Test Tag")
        auth_token = generate_token(
            users_factories.UserFactory(), [perm for perm in Permissions if perm != Permissions.MANAGE_PRO_ENTITY]
        )

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.add_tag_to_offerer", offerer_id=offerer.id, tag_name=tag.name)
        )

        # then
        assert response.status_code == 403
        offerer_tag_mapping = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_tag_mapping) == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_add_tag_to_offerer_as_anonymous(self, client):
        # given
        offerer = offerers_factories.OffererFactory()
        tag = offerers_factories.OffererTagFactory(name="test-tag", label="Test Tag")

        # when
        response = client.post(
            url_for("backoffice_blueprint.add_tag_to_offerer", offerer_id=offerer.id, tag_name=tag.name)
        )

        # then
        assert response.status_code == 403
        offerer_tag_mapping = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_tag_mapping) == 0


class RemoveOffererTagTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_remove_tag_from_offerer(self, client):
        # given
        offerer1 = offerers_factories.OffererFactory()
        offerer2 = offerers_factories.OffererFactory()
        tag1 = offerers_factories.OffererTagFactory(name="test-top-acteur", label="Top acteur")
        tag2 = offerers_factories.OffererTagFactory(name="test-type-ei", label="Entreprise individuelle")
        mapping1 = offerers_factories.OffererTagMappingFactory(offererId=offerer1.id, tagId=tag1.id)
        mapping2 = offerers_factories.OffererTagMappingFactory(offererId=offerer1.id, tagId=tag2.id)
        mapping3 = offerers_factories.OffererTagMappingFactory(offererId=offerer2.id, tagId=tag1.id)
        mapping4 = offerers_factories.OffererTagMappingFactory(offererId=offerer2.id, tagId=tag2.id)
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.MANAGE_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).delete(
            url_for("backoffice_blueprint.remove_tag_from_offerer", offerer_id=offerer1.id, tag_name=tag2.name)
        )

        # then
        assert response.status_code == 204
        offerer_tag_mapping = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_tag_mapping) == 3
        mapping_ids = {item.id for item in offerer_tag_mapping}
        assert mapping1.id in mapping_ids
        assert mapping2.id not in mapping_ids
        assert mapping3.id in mapping_ids
        assert mapping4.id in mapping_ids

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_remove_tag_from_offerer_when_not_mapped(self, client):
        # given
        offerer = offerers_factories.OffererFactory()
        tag = offerers_factories.OffererTagFactory(name="test-tag", label="Test Tag")
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.MANAGE_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).delete(
            url_for("backoffice_blueprint.remove_tag_from_offerer", offerer_id=offerer.id, tag_name=tag.name)
        )

        # then
        assert response.status_code == 404
        assert response.json["tag_name"] == "L'association structure - tag n'existe pas"
        offerer_tag_mapping = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_tag_mapping) == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_remove_unexisting_tag_from_offerer(self, client):
        # given
        offerer = offerers_factories.OffererFactory()
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.MANAGE_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).delete(
            url_for("backoffice_blueprint.remove_tag_from_offerer", offerer_id=offerer.id, tag_name="does-not-exist")
        )

        # then
        assert response.status_code == 404
        assert response.json["tag_name"] == "L'association structure - tag n'existe pas"
        offerer_tag_mapping = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_tag_mapping) == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_remove_tag_from_unexisting_offerer(self, client):
        # given
        tag = offerers_factories.OffererTagFactory(name="test-tag", label="Test Tag")
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.MANAGE_PRO_ENTITY])

        # when
        response = client.with_explicit_token(auth_token).delete(
            url_for("backoffice_blueprint.remove_tag_from_offerer", offerer_id=42, tag_name=tag.name)
        )

        # then
        assert response.status_code == 404
        assert response.json["tag_name"] == "L'association structure - tag n'existe pas"
        offerer_tag_mapping = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_tag_mapping) == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_remove_tag_from_offerer_without_permission(self, client):
        # given
        offerer = offerers_factories.OffererFactory()
        tag = offerers_factories.OffererTagFactory(name="test-tag", label="Test Tag")
        mapping = offerers_factories.OffererTagMappingFactory(offererId=offerer.id, tagId=tag.id)
        auth_token = generate_token(
            users_factories.UserFactory(), [perm for perm in Permissions if perm != Permissions.MANAGE_PRO_ENTITY]
        )

        # when
        response = client.with_explicit_token(auth_token).delete(
            url_for("backoffice_blueprint.remove_tag_from_offerer", offerer_id=offerer.id, tag_name=tag.name)
        )

        # then
        assert response.status_code == 403
        offerer_tag_mapping = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_tag_mapping) == 1
        assert offerer_tag_mapping[0].id == mapping.id

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_remove_tag_from_offerer_as_anonymous(self, client):
        # given
        offerer = offerers_factories.OffererFactory()
        tag = offerers_factories.OffererTagFactory(name="test-tag", label="Test Tag")
        mapping = offerers_factories.OffererTagMappingFactory(offererId=offerer.id, tagId=tag.id)

        # when
        response = client.delete(
            url_for("backoffice_blueprint.remove_tag_from_offerer", offerer_id=offerer.id, tag_name=tag.name)
        )

        # then
        assert response.status_code == 403
        offerer_tag_mapping = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_tag_mapping) == 1
        assert offerer_tag_mapping[0].id == mapping.id


class OfferersStatsTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_offerer_stats(self, client):
        # given
        offerers_factories.UserOffererFactory(offerer__validationStatus=ValidationStatus.NEW)
        offerers_factories.UserOffererFactory.create_batch(2, offerer__validationStatus=ValidationStatus.PENDING)
        offerers_factories.UserOffererFactory.create_batch(3, offerer__validationStatus=ValidationStatus.VALIDATED)
        offerers_factories.UserOffererFactory.create_batch(4, offerer__validationStatus=ValidationStatus.REJECTED)
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.VALIDATE_OFFERER])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(url_for("backoffice_blueprint.get_offerers_stats"))

        # then
        assert response.status_code == 200
        data = response.json["data"]
        assert data == {"NEW": 1, "PENDING": 2, "VALIDATED": 3, "REJECTED": 4}

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_offerer_stats_zero(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.VALIDATE_OFFERER])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(url_for("backoffice_blueprint.get_offerers_stats"))

        # then
        assert response.status_code == 200
        data = response.json["data"]
        assert data == {"NEW": 0, "PENDING": 0, "VALIDATED": 0, "REJECTED": 0}

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_stats_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [perm for perm in Permissions if perm != Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).get(url_for("backoffice_blueprint.get_offerers_stats"))

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_offerer_stats_as_anonymous(self, client):
        # given
        offerers_factories.UserNotValidatedOffererFactory()

        # when
        response = client.get(url_for("backoffice_blueprint.get_offerers_stats"))

        # then
        assert response.status_code == 403


class ListOfferersToBeValidatedTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_list_only_offerers_to_be_validated(self, client):
        # given
        _validated_offerers = [offerers_factories.UserOffererFactory().offerer for _ in range(3)]
        to_be_validated_offerers = []
        for _ in range(4):
            user_offerer = offerers_factories.UserNotValidatedOffererFactory()
            history_factories.ActionHistoryFactory(
                actionType=history_models.ActionType.OFFERER_NEW,
                authorUser=users_factories.AdminFactory(),
                offerer=user_offerer.offerer,
                user=user_offerer.user,
                comment=None,
            )
            to_be_validated_offerers.append(user_offerer.offerer)

        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for("backoffice_blueprint.list_offerers_to_be_validated")
            )

        # then
        assert response.status_code == 200
        data = response.json["data"]
        assert sorted(d["id"] for d in data) == sorted(o.id for o in to_be_validated_offerers)

    @pytest.mark.parametrize(
        "validation_status,expected_status",
        [
            (ValidationStatus.NEW, ValidationStatus.NEW.value),
            (ValidationStatus.PENDING, ValidationStatus.PENDING.value),
        ],
    )
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_payload_content(self, client, validation_status, expected_status):
        # given
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(
            offerer__dateCreated=datetime.datetime(2022, 10, 3, 11, 59), offerer__validationStatus=validation_status
        )
        commenter = users_factories.AdminFactory(firstName="Inspecteur", lastName="Validateur")
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 3, 12, 0),
            actionType=history_models.ActionType.OFFERER_NEW,
            authorUser=commenter,
            offerer=user_offerer.offerer,
            user=user_offerer.user,
            comment=None,
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 3, 13, 1),
            actionType=history_models.ActionType.COMMENT,
            authorUser=commenter,
            offerer=user_offerer.offerer,
            comment="Bla blabla",
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 3, 14, 2),
            actionType=history_models.ActionType.OFFERER_PENDING,
            authorUser=commenter,
            offerer=user_offerer.offerer,
            comment="Houlala",
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 10, 3, 15, 3),
            actionType=history_models.ActionType.USER_OFFERER_VALIDATED,
            authorUser=commenter,
            offerer=user_offerer.offerer,
            user=user_offerer.user,
            comment=None,
        )
        tag = offerers_factories.OffererTagFactory(name="top-acteur", label="Top Actor")

        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for("backoffice_blueprint.list_offerers_to_be_validated")
            )

        # then
        assert response.status_code == 200
        payload = response.json["data"][0]
        assert payload["id"] == user_offerer.offerer.id
        assert payload["name"] == user_offerer.offerer.name
        assert payload["dateCreated"] == "2022-10-03T11:59:00Z"
        assert payload["status"] == expected_status
        assert payload["step"] is None  # TODO
        assert payload["siren"] == user_offerer.offerer.siren
        assert payload["address"] == user_offerer.offerer.address
        assert payload["postalCode"] == user_offerer.offerer.postalCode
        assert payload["city"] == user_offerer.offerer.city
        assert payload["owner"] == " ".join(
            (
                user_offerer.offerer.first_user.firstName,
                user_offerer.offerer.first_user.lastName,
            )
        )
        assert payload["ownerId"] == user_offerer.offerer.first_user.id
        assert payload["phoneNumber"] == user_offerer.offerer.first_user.phoneNumber
        assert payload["email"] == user_offerer.offerer.first_user.email
        assert payload["lastComment"] == {
            "author": "Inspecteur Validateur",
            "content": "Houlala",
            "date": "2022-10-03T14:02:00Z",
        }
        assert payload["isTopActor"] == (tag in user_offerer.offerer.tags)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_payload_content_no_action(self, client):
        # given
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(
            offerer__dateCreated=datetime.datetime(2022, 10, 3, 11, 59),
        )

        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for("backoffice_blueprint.list_offerers_to_be_validated")
            )

        # then
        assert response.status_code == 200
        payload = response.json["data"][0]
        assert payload["id"] == user_offerer.offerer.id
        assert payload["name"] == user_offerer.offerer.name
        assert payload["dateCreated"] == "2022-10-03T11:59:00Z"
        assert payload["status"] == "NEW"
        assert payload["step"] is None  # TODO
        assert payload["lastComment"] is None
        assert payload["isTopActor"] is False

    @override_features(ENABLE_BACKOFFICE_API=True)
    @pytest.mark.parametrize(
        "total_items, pagination_config, expected_total_pages, expected_page, expected_items",
        (
            (10, {"perPage": 3}, 4, 1, 3),
            (10, {"perPage": 3, "page": 1}, 4, 1, 3),
            (10, {"perPage": 3, "page": 3}, 4, 3, 3),
            (10, {"perPage": 3, "page": 4}, 4, 4, 1),
            (10, {"perPage": 5, "page": 1}, 2, 1, 5),
            (10, {"page": 1}, 1, 1, 10),
            (10, {"perPage": 20, "page": 1}, 1, 1, 10),
        ),
    )
    def test_list_pagination(
        self, client, total_items, pagination_config, expected_total_pages, expected_page, expected_items
    ):
        # given
        _validated_offerers = [offerers_factories.UserNotValidatedOffererFactory().offerer for i in range(total_items)]

        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.list_offerers_to_be_validated", **pagination_config)
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == expected_items
        assert response.json["pages"] == expected_total_pages
        assert response.json["total"] == total_items
        assert response.json["page"] == expected_page

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_list_sorting(self, client):
        # given
        offerer_1 = offerers_factories.UserNotValidatedOffererFactory(
            offerer__name="A",
            offerer__dateCreated=datetime.datetime.utcnow() - datetime.timedelta(hours=1),
        ).offerer
        offerer_2 = offerers_factories.UserNotValidatedOffererFactory(
            offerer__name="B", offerer__dateCreated=datetime.datetime.utcnow()
        ).offerer
        offerer_3 = offerers_factories.UserNotValidatedOffererFactory(
            offerer__name="C",
            offerer__dateCreated=datetime.datetime.utcnow() - datetime.timedelta(hours=2),
        ).offerer

        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        name_asc = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.list_offerers_to_be_validated", sort='[{"field": "name"}]')
        )
        creation_date_desc = client.with_explicit_token(auth_token).get(
            url_for(
                "backoffice_blueprint.list_offerers_to_be_validated", sort='[{"field": "dateCreated", "order": "desc"}]'
            )
        )

        # then
        assert name_asc.status_code == 200
        assert [o["id"] for o in name_asc.json["data"]] == [o.id for o in (offerer_1, offerer_2, offerer_3)]
        assert creation_date_desc.status_code == 200
        assert [o["id"] for o in creation_date_desc.json["data"]] == [o.id for o in (offerer_2, offerer_1, offerer_3)]

    @override_features(ENABLE_BACKOFFICE_API=True)
    @pytest.mark.parametrize(
        "tag_filter, expected_offerer_names",
        (
            (["Top acteur"], ["B", "E", "F"]),
            (["Collectivité"], ["C", "E"]),
            (["Établissement public"], ["D", "F"]),
            (["Établissement public", "Top acteur"], ["F"]),
        ),
    )
    def test_list_filtering_by_tags(self, client, tag_filter, expected_offerer_names, offerers_to_be_validated):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for(
                    "backoffice_blueprint.list_offerers_to_be_validated",
                    filter=json.dumps([{"field": "tags", "value": tag_filter}]),
                )
            )

        # then
        assert response.status_code == 200
        data = response.json["data"]
        assert sorted(o["name"] for o in data) == sorted(expected_offerer_names)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_list_filtering_by_date(self, client):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # Created before requested range, excluded from results:
        user_offerer_2 = offerers_factories.UserNotValidatedOffererFactory(
            offerer__dateCreated=datetime.datetime(2022, 11, 4, 4)
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 11, 4, 4),
            actionType=history_models.ActionType.OFFERER_NEW,
            authorUser=user_offerer_2.user,
            offerer=user_offerer_2.offerer,
            user=user_offerer_2.user,
        )
        # Created within requested range:
        user_offerer_3 = offerers_factories.UserNotValidatedOffererFactory(
            offerer__dateCreated=datetime.datetime(2022, 11, 6, 5)
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 11, 6, 5),
            actionType=history_models.ActionType.OFFERER_NEW,
            authorUser=user_offerer_3.user,
            offerer=user_offerer_3.offerer,
            user=user_offerer_3.user,
        )
        # No history, in requested range:
        user_offerer_4 = offerers_factories.UserNotValidatedOffererFactory(
            offerer__dateCreated=datetime.datetime(2022, 11, 8, 6)
        )
        # No history, excluded from results:
        offerers_factories.UserNotValidatedOffererFactory(offerer__dateCreated=datetime.datetime(2022, 11, 10, 7))

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for(
                    "backoffice_blueprint.list_offerers_to_be_validated",
                    filter=json.dumps(
                        [{"field": "fromDate", "value": "2022-11-05"}, {"field": "toDate", "value": "2022-11-08"}]
                    ),
                )
            )

        # then
        assert response.status_code == 200
        assert {o["id"] for o in response.json["data"]} == {uo.offerer.id for uo in (user_offerer_3, user_offerer_4)}

    @pytest.mark.parametrize(
        "dates_filter",
        [
            '[{"field": "fromDate", "value": "05/11/2022"}, {"field": "toDate", "value": "2022-11-08"}]',
            '[{"field": "fromDate", "value": "2022-11-05"}, {"field": "toDate", "value": "08/11/2022"}]',
            '[{"field": "fromDate", "value": "2022-11-05T12:34:56"}, {"field": "toDate", "value": "2022-11-08T01:23:45"}]',
        ],
    )
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_list_filtering_by_invalid_date(self, client, dates_filter):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        response = client.with_explicit_token(auth_token).get(
            url_for(
                "backoffice_blueprint.list_offerers_to_be_validated",
                filter=json.dumps(
                    [{"field": "fromDate", "value": "05/11/2022"}, {"field": "toDate", "value": "08/11/2022"}]
                ),
            )
        )

        # then
        assert response.status_code == 400
        assert response.json["filter"] == "Le format de date est invalide"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_list_search_by_siren(self, client, offerers_to_be_validated):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for("backoffice_blueprint.list_offerers_to_be_validated", q="123004004")
            )

        # then
        assert response.status_code == 200
        data = response.json["data"]
        assert len(data) == 1
        assert data[0]["name"] == "D"

    @override_features(ENABLE_BACKOFFICE_API=True)
    @pytest.mark.parametrize("siren", ["12345678", "1234567890"])
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_list_search_by_invalid_siren(self, client, siren):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.list_offerers_to_be_validated", q=siren)
        )

        # then
        assert response.status_code == 400
        assert response.json["q"] == "Le SIREN doit faire 9 caractères"

    @override_features(ENABLE_BACKOFFICE_API=True)
    @pytest.mark.parametrize(
        "search_filter, expected_offerer_names",
        (
            ("cinema de la plage", ["Cinéma de la Petite Plage", "Cinéma de la Grande Plage"]),
            ("cinéma", ["Cinéma de la Petite Plage", "Cinéma de la Grande Plage", "Cinéma du Centre"]),
            ("Plage", ["Librairie de la Plage", "Cinéma de la Petite Plage", "Cinéma de la Grande Plage"]),
            ("Librairie du Centre", []),
        ),
    )
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_list_search_by_name(self, search_filter, expected_offerer_names, client):
        # given
        for name in (
            "Librairie de la Plage",
            "Cinéma de la Petite Plage",
            "Cinéma du Centre",
            "Cinéma de la Grande Plage",
        ):
            offerers_factories.NotValidatedOffererFactory(name=name)
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for("backoffice_blueprint.list_offerers_to_be_validated", q=search_filter)
            )

        # then
        assert response.status_code == 200
        data = response.json["data"]
        assert len(data) == len(expected_offerer_names)
        assert sorted(o["name"] for o in data) == sorted(expected_offerer_names)

    @override_features(ENABLE_BACKOFFICE_API=True)
    @pytest.mark.parametrize(
        "status_filter, expected_offerer_names",
        (
            (["NEW"], ["A", "C", "E"]),
            (["PENDING"], ["B", "D", "F"]),
            (["NEW", "PENDING"], ["A", "B", "C", "D", "E", "F"]),
            (["VALIDATED"], ["G"]),
            (["REJECTED"], ["H"]),
            ([], ["A", "B", "C", "D", "E", "F"]),  # same as default
            (["OTHER"], []),  # unknown value
            (["REJECTED", "OTHER"], ["H"]),  # only valid value taken into account
        ),
    )
    def test_list_filtering_by_status(self, client, status_filter, expected_offerer_names, offerers_to_be_validated):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for(
                    "backoffice_blueprint.list_offerers_to_be_validated",
                    filter=json.dumps([{"field": "status", "value": status_filter}]),
                )
            )

        # then
        assert response.status_code == 200
        data = response.json["data"]
        assert sorted(o["name"] for o in data) == sorted(expected_offerer_names)

    @override_features(ENABLE_BACKOFFICE_API=True)
    @pytest.mark.parametrize(
        "sorts",
        (
            "this is not even a JSON string",
            '{"field": "id"}',  # not a list
            '[{"field": "fancifulField"}]',
            '[{"order": "asc"}]',
        ),
    )
    def test_fanciful_filtering_return_a_400_status(self, client, sorts):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.list_offerers_to_be_validated", sort=sorts)
        )

        # then
        assert response.status_code == 400

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_list_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [perm for perm in Permissions if perm != Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.list_offerers_to_be_validated")
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_list_as_anonymous(self, client):
        # given
        offerers_factories.UserNotValidatedOffererFactory()

        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.list_offerers_to_be_validated")
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_with_top_actor_tag_is_top_actor(self, client):
        # given
        admin = users_factories.UserFactory()
        tag = offerers_factories.OffererTagFactory(name="top-acteur", label="Top Actor")
        offerer = offerers_factories.UserNotValidatedOffererFactory().offerer

        # the offerer has no top-acteur tag
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.list_offerers_to_be_validated")
        )
        assert response.status_code == 200
        assert response.json["data"][0]["isTopActor"] is False

        # add top-acteur tag
        auth_token = generate_token(admin, [Permissions.MANAGE_PRO_ENTITY])
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.add_tag_to_offerer", offerer_id=offerer.id, tag_name=tag.name)
        )

        # when
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.list_offerers_to_be_validated")
        )

        # then
        assert response.status_code == 200
        assert response.json["data"][0]["isTopActor"] is True

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_offerer_without_top_actor_tag_is_not_top_actor(self, client):
        # given
        # we create a tag and add it to the offerer
        admin = users_factories.UserFactory()
        tag = offerers_factories.OffererTagFactory(name="hello-world-tag", label="Hello World")
        offerer = offerers_factories.UserNotValidatedOffererFactory().offerer

        auth_token = generate_token(admin, [Permissions.MANAGE_PRO_ENTITY])
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.add_tag_to_offerer", offerer_id=offerer.id, tag_name=tag.name)
        )

        # when
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.list_offerers_to_be_validated")
        )

        # then
        assert response.status_code == 200
        assert response.json["data"][0]["isTopActor"] is False


class ValidateOffererAttachmentTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_validate_offerer_attachment(self, client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.validate_offerer_attachment", user_offerer_id=user_offerer.id)
        )

        # then
        assert response.status_code == 204
        db.session.refresh(user_offerer)
        assert user_offerer.isValidated
        assert user_offerer.user.has_pro_role

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_OFFERER_VALIDATED
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_validate_offerer_attachment_returns_404_if_offerer_is_not_found(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.validate_offerer_attachment", user_offerer_id=42)
        )

        # then
        assert response.status_code == 404
        assert response.json["user_offerer_id"] == "Le rattachement n'existe pas"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannotvalidate_offerer_attachment_already_validated(self, client):
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.validate_offerer_attachment", user_offerer_id=user_offerer.id)
        )

        # then
        assert response.status_code == 400
        assert response.json["user_offerer_id"] == "Le rattachement est déjà validé"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannotvalidate_offerer_attachment_without_permission(self, client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()
        auth_token = generate_token(
            users_factories.UserFactory(), [perm for perm in Permissions if perm != Permissions.VALIDATE_OFFERER]
        )

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.validate_offerer_attachment", user_offerer_id=user_offerer.id)
        )

        # then
        assert response.status_code == 403
        db.session.refresh(user_offerer)
        assert not user_offerer.isValidated
        assert history_models.ActionHistory.query.count() == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannotvalidate_offerer_attachment_as_anonymous(self, client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # when
        response = client.post(
            url_for("backoffice_blueprint.validate_offerer_attachment", user_offerer_id=user_offerer.id)
        )

        # then
        assert response.status_code == 403
        db.session.refresh(user_offerer)
        assert not user_offerer.isValidated
        assert history_models.ActionHistory.query.count() == 0


class RejectOffererAttachmentTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_reject_offerer_attachment(self, client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.reject_offerer_attachment", user_offerer_id=user_offerer.id)
        )

        # then
        assert response.status_code == 204
        users_offerers = offerers_models.UserOfferer.query.all()
        assert len(users_offerers) == 0

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_OFFERER_REJECTED
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_reject_offerer_returns_404_if_offerer_attachment_is_not_found(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory(), [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.reject_offerer_attachment", user_offerer_id=42)
        )

        # then
        assert response.status_code == 404
        assert response.json["user_offerer_id"] == "Le rattachement n'existe pas"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_reject_offerer_attachment_without_permission(self, client):
        # given
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()
        auth_token = generate_token(
            users_factories.UserFactory(), [perm for perm in Permissions if perm != Permissions.VALIDATE_OFFERER]
        )

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.reject_offerer_attachment", user_offerer_id=user_offerer.id)
        )

        # then
        assert response.status_code == 403
        db.session.refresh(user_offerer)
        users_offerers = offerers_models.UserOfferer.query.all()
        assert len(users_offerers) == 1
        assert history_models.ActionHistory.query.count() == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_reject_offerer_attachment_as_anonymous(self, client):
        # given
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        # when
        response = client.post(
            url_for("backoffice_blueprint.reject_offerer_attachment", user_offerer_id=user_offerer.id)
        )

        # then
        assert response.status_code == 403
        db.session.refresh(user_offerer)
        users_offerers = offerers_models.UserOfferer.query.all()
        assert len(users_offerers) == 1
        assert history_models.ActionHistory.query.count() == 0


class SetOffererAttachmentPendingTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_set_offerer_attachment_pending(self, client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.set_offerer_attachment_pending", user_offerer_id=user_offerer.id),
            json={"comment": "En attente de documents"},
        )

        # then
        assert response.status_code == 204
        db.session.refresh(user_offerer)
        assert not user_offerer.isValidated
        assert user_offerer.validationStatus == ValidationStatus.PENDING
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_OFFERER_PENDING
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None
        assert action.comment == "En attente de documents"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_set_offerer_pending_without_permission(self, client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()
        auth_token = generate_token(
            users_factories.UserFactory(), [perm for perm in Permissions if perm != Permissions.VALIDATE_OFFERER]
        )

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.set_offerer_attachment_pending", user_offerer_id=user_offerer.id),
            json={"comment": "Test"},
        )

        # then
        assert response.status_code == 403
        assert user_offerer.validationStatus == ValidationStatus.NEW
        assert history_models.ActionHistory.query.count() == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_set_offerer_pending_as_anonymous(self, client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # when
        response = client.post(
            url_for("backoffice_blueprint.set_offerer_attachment_pending", user_offerer_id=user_offerer.id),
            json={"comment": "Test"},
        )

        # then
        assert response.status_code == 403
        assert user_offerer.validationStatus == ValidationStatus.NEW
        assert history_models.ActionHistory.query.count() == 0


class CommentOffererAttachmentTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_comment_offerer_attchment(self, client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.comment_offerer_attachment", user_offerer_id=user_offerer.id),
            json={"comment": "Code APE non éligible"},
        )

        # then
        assert response.status_code == 204
        db.session.refresh(user_offerer)
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.COMMENT
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None
        assert action.comment == "Code APE non éligible"

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_comment_offerer_attachment_without_permission(self, client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()
        auth_token = generate_token(
            users_factories.UserFactory(), [perm for perm in Permissions if perm != Permissions.VALIDATE_OFFERER]
        )

        # when
        response = client.with_explicit_token(auth_token).post(
            url_for("backoffice_blueprint.comment_offerer_attachment", user_offerer_id=user_offerer.id),
            json={"comment": "Test"},
        )

        # then
        assert response.status_code == 403
        assert history_models.ActionHistory.query.count() == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_comment_offerer_attachment_as_anonymous(self, client):
        # given
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # when
        response = client.post(
            url_for("backoffice_blueprint.comment_offerer_attachment", user_offerer_id=user_offerer.id),
            json={"comment": "Test"},
        )

        # then
        assert response.status_code == 403
        assert history_models.ActionHistory.query.count() == 0


class ToggleTopActorTagTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_toggle_is_top_actor(self, client):
        # given
        admin = users_factories.UserFactory()
        offerer = offerers_factories.UserNotValidatedOffererFactory().offerer
        tag = offerers_factories.OffererTagFactory(name="top-acteur", label="Top acteur")

        # when
        auth_token = generate_token(admin, [Permissions.MANAGE_PRO_ENTITY])
        response = client.with_explicit_token(auth_token).put(
            url_for("backoffice_blueprint.toggle_top_actor", offerer_id=offerer.id), json={"isTopActor": True}
        )

        # then
        assert response.status_code == 204
        offerer_mappings = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_mappings) == 1
        assert offerer_mappings[0].tagId == tag.id
        assert offerer_mappings[0].offererId == offerer.id

        # when
        auth_token = generate_token(admin, [Permissions.MANAGE_PRO_ENTITY])
        response = client.with_explicit_token(auth_token).put(
            url_for("backoffice_blueprint.toggle_top_actor", offerer_id=offerer.id), json={"isTopActor": False}
        )

        # then
        assert response.status_code == 204
        assert offerers_models.OffererTagMapping.query.count() == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_toggle_is_top_actor_twice_true(self, client):
        # given
        admin = users_factories.UserFactory()
        offerer = offerers_factories.UserNotValidatedOffererFactory().offerer
        tag = offerers_factories.OffererTagFactory(name="top-acteur", label="Top acteur")

        # when
        auth_token = generate_token(admin, [Permissions.MANAGE_PRO_ENTITY])
        for _ in range(2):
            response = client.with_explicit_token(auth_token).put(
                url_for("backoffice_blueprint.toggle_top_actor", offerer_id=offerer.id), json={"isTopActor": True}
            )

            # then
            assert response.status_code == 204

        # then
        offerer_mappings = offerers_models.OffererTagMapping.query.all()
        assert len(offerer_mappings) == 1
        assert offerer_mappings[0].tagId == tag.id
        assert offerer_mappings[0].offererId == offerer.id


class ListUserOffererToBeValidatedTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_list_only_user_offerer_to_be_validated(self, client):
        # given
        to_be_validated = []
        for _ in range(2):
            validated_user_offerer = offerers_factories.UserOffererFactory()
            new_user_offerer = offerers_factories.NotValidatedUserOffererFactory(offerer=validated_user_offerer.offerer)
            to_be_validated.append(new_user_offerer)
            pending_user_offerer = offerers_factories.NotValidatedUserOffererFactory(
                offerer=validated_user_offerer.offerer, validationStatus=ValidationStatus.PENDING
            )
            to_be_validated.append(pending_user_offerer)
            for action_type in (
                history_models.ActionType.USER_OFFERER_PENDING,
                history_models.ActionType.USER_OFFERER_PENDING,
            ):
                history_factories.ActionHistoryFactory(
                    actionType=action_type,
                    authorUser=users_factories.AdminFactory(),
                    offerer=pending_user_offerer.offerer,
                    user=pending_user_offerer.user,
                    comment=None,
                )

        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for("backoffice_blueprint.list_offerers_attachments_to_be_validated")
            )

        # then
        assert response.status_code == 200
        data = response.json["data"]
        assert sorted(d["id"] for d in data) == sorted(o.id for o in to_be_validated)

    @pytest.mark.parametrize(
        "validation_status,expected_status",
        [
            (ValidationStatus.NEW, ValidationStatus.NEW.value),
            (ValidationStatus.PENDING, ValidationStatus.PENDING.value),
        ],
    )
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_payload_content(self, client, validation_status, expected_status):
        # given
        owner_user_offerer = offerers_factories.UserOffererFactory(
            offerer__dateCreated=datetime.datetime(2022, 11, 2, 11, 30)
        )
        new_user_offerer = offerers_factories.NotValidatedUserOffererFactory(
            offerer=owner_user_offerer.offerer,
            validationStatus=validation_status,
            dateCreated=datetime.datetime(2022, 11, 3, 12, 0),
        )
        commenter = users_factories.AdminFactory(firstName="Inspecteur", lastName="Validateur")
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 11, 3, 12, 0),
            actionType=history_models.ActionType.USER_OFFERER_NEW,
            authorUser=commenter,
            offerer=new_user_offerer.offerer,
            user=new_user_offerer.user,
            comment=None,
        )
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2022, 11, 3, 13, 1),
            actionType=history_models.ActionType.COMMENT,
            authorUser=commenter,
            offerer=new_user_offerer.offerer,
            user=new_user_offerer.user,
            comment="Bla blabla",
        )
        if validation_status == ValidationStatus.PENDING:
            history_factories.ActionHistoryFactory(
                actionDate=datetime.datetime(2022, 11, 3, 14, 2),
                actionType=history_models.ActionType.USER_OFFERER_PENDING,
                authorUser=commenter,
                offerer=new_user_offerer.offerer,
                comment=None,
            )

        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for("backoffice_blueprint.list_offerers_attachments_to_be_validated")
            )

        # then
        assert response.status_code == 200
        payload = response.json["data"][0]
        assert payload["id"] == new_user_offerer.id
        assert payload["userId"] == new_user_offerer.userId
        assert payload["email"] == new_user_offerer.user.email
        assert payload["userName"] == new_user_offerer.user.full_name
        assert payload["status"] == expected_status
        assert payload["dateCreated"] == "2022-11-03T12:00:00Z"
        assert payload["lastComment"] == {
            "author": "Inspecteur Validateur",
            "content": "Bla blabla",
            "date": "2022-11-03T13:01:00Z",
        }
        assert payload["phoneNumber"] == new_user_offerer.user.phoneNumber
        assert payload["offererId"] == owner_user_offerer.offerer.id
        assert payload["offererName"] == owner_user_offerer.offerer.name
        assert payload["offererCreatedDate"] == "2022-11-02T11:30:00Z"
        assert payload["ownerId"] == owner_user_offerer.user.id
        assert payload["ownerEmail"] == owner_user_offerer.user.email
        assert payload["siren"] == owner_user_offerer.offerer.siren

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_payload_content_no_action(self, client):
        # given
        owner_user_offerer = offerers_factories.UserOffererFactory(offerer__dateCreated=datetime.datetime(2022, 11, 3))
        offerers_factories.UserOffererFactory(offerer=owner_user_offerer.offerer)  # other validated, not owner
        new_user_offerer = offerers_factories.NotValidatedUserOffererFactory(
            offerer=owner_user_offerer.offerer,
            dateCreated=datetime.datetime(2022, 11, 25, 12, 34),
        )

        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for("backoffice_blueprint.list_offerers_attachments_to_be_validated")
            )

        # then
        assert response.status_code == 200
        payload = response.json["data"][0]
        assert payload["id"] == new_user_offerer.id
        assert payload["userId"] == new_user_offerer.userId
        assert payload["email"] == new_user_offerer.user.email
        assert payload["userName"] == new_user_offerer.user.full_name
        assert payload["status"] == ValidationStatus.NEW.value
        assert payload["dateCreated"] == "2022-11-25T12:34:00Z"
        assert payload["lastComment"] is None
        assert payload["phoneNumber"] == new_user_offerer.user.phoneNumber
        assert payload["offererId"] == owner_user_offerer.offerer.id
        assert payload["offererName"] == owner_user_offerer.offerer.name
        assert payload["offererCreatedDate"] == "2022-11-03T00:00:00Z"
        assert payload["ownerId"] == owner_user_offerer.user.id
        assert payload["ownerEmail"] == owner_user_offerer.user.email
        assert payload["siren"] == owner_user_offerer.offerer.siren

    @override_features(ENABLE_BACKOFFICE_API=True)
    @pytest.mark.parametrize(
        "total_items, pagination_config, expected_total_pages, expected_page, expected_items",
        (
            (10, {"perPage": 3}, 4, 1, 3),
            (10, {"perPage": 3, "page": 1}, 4, 1, 3),
            (10, {"perPage": 3, "page": 3}, 4, 3, 3),
            (10, {"perPage": 3, "page": 4}, 4, 4, 1),
            (10, {"perPage": 5, "page": 1}, 2, 1, 5),
            (10, {"page": 1}, 1, 1, 10),
            (10, {"perPage": 20, "page": 1}, 1, 1, 10),
        ),
    )
    def test_list_pagination(
        self, client, total_items, pagination_config, expected_total_pages, expected_page, expected_items
    ):
        # given
        _ = [offerers_factories.NotValidatedUserOffererFactory().offerer for i in range(total_items)]

        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.list_offerers_attachments_to_be_validated", **pagination_config)
        )

        # then
        assert response.status_code == 200
        assert len(response.json["data"]) == expected_items
        assert response.json["pages"] == expected_total_pages
        assert response.json["total"] == total_items
        assert response.json["page"] == expected_page

    @override_features(ENABLE_BACKOFFICE_API=True)
    @pytest.mark.parametrize(
        "status_filter, expected_users_emails",
        (
            (["NEW"], ["a@example.com", "c@example.com", "e@example.com"]),
            (["PENDING"], ["b@example.com", "d@example.com", "f@example.com"]),
            (
                ["NEW", "PENDING"],
                ["a@example.com", "b@example.com", "c@example.com", "d@example.com", "e@example.com", "f@example.com"],
            ),
            (["VALIDATED"], ["g@example.com"]),
            (["REJECTED"], []),
            (
                [],
                ["a@example.com", "b@example.com", "c@example.com", "d@example.com", "e@example.com", "f@example.com"],
            ),  # same as default
            (["OTHER"], []),  # unknown value
        ),
    )
    def test_list_filtering_by_status(self, client, status_filter, expected_users_emails, user_offerer_to_be_validated):
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.VALIDATE_OFFERER])

        # when
        with assert_no_duplicated_queries():
            response = client.with_explicit_token(auth_token).get(
                url_for(
                    "backoffice_blueprint.list_offerers_attachments_to_be_validated",
                    filter=json.dumps([{"field": "status", "value": status_filter}]),
                )
            )

        # then
        assert response.status_code == 200
        data = response.json["data"]
        assert sorted(o["email"] for o in data) == sorted(expected_users_emails)

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_list_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [perm for perm in Permissions if perm != Permissions.VALIDATE_OFFERER])

        # when
        response = client.with_explicit_token(auth_token).get(
            url_for("backoffice_blueprint.list_offerers_attachments_to_be_validated")
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_list_as_anonymous(self, client):
        # given
        offerers_factories.NotValidatedUserOffererFactory()

        # when
        response = client.get(url_for("backoffice_blueprint.list_offerers_attachments_to_be_validated"))

        # then
        assert response.status_code == 403
