from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models


def create_users_offerers() -> list[offerers_models.Offerer]:
    offeres = []
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_1_lieu@example.com",
        offerer__name="eac_1_lieu",
    )
    offeres.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_2_lieu@example.com",
        offerer__name="eac_2_lieu [BON EAC]",
        offerer__siren="123456782",
    )
    offeres.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="squad-eac@passculture.app",
        offerer=user_offerer.offerer,
    )

    # user with 2 offerer 1 eac and 1 non eac
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="half_eac@example.com",
        offerer=user_offerer.offerer,
    )
    offerers_factories.UserOffererFactory(
        user=user_offerer.user,
        offerer__name="no_eac",
    )

    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_pending_bank_informations@example.com",
        offerer__name="eac_pending_bank_informations",
    )
    offeres.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_no_cb@example.com",
        offerer__name="eac_no_cb",
    )
    offeres.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="eac_rejected@example.com",
        offerer__name="eac_rejected",
    )
    offeres.append(user_offerer.offerer)
    user_offerer = offerers_factories.UserOffererFactory(
        user__email="pending_eac@example.com",
        offerer__name="pending_eac",
    )
    offeres.append(user_offerer.offerer)

    return offeres
