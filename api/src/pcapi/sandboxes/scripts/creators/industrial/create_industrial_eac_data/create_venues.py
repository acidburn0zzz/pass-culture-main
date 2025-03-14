from datetime import datetime
from datetime import timedelta
from itertools import chain
from itertools import count
from itertools import cycle

from pcapi.core.educational import factories as educational_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models


MAINLAND_INTERVENTION_AREA = [str(i).zfill(2) for i in chain(range(1, 95), ["2A", "2B", "mainland"]) if i != 20]
ALL_INTERVENTION_AREA = [
    *MAINLAND_INTERVENTION_AREA,
    "971",
    "972",
    "973",
    "974",
    "975",
    "976",
    "all",
]


VENUE_EDUCATIONAL_STATUS = {
    2: "Établissement public",
    3: "Association",
    4: "Établissement privé",
    5: "micro-entreprise, auto-entrepreneur",
}


def create_venues(offerer_list: list[offerers_models.Offerer]) -> None:
    create_venue_educational_status()
    offerer_iterator = iter(offerer_list)
    educational_status_iterator = cycle(VENUE_EDUCATIONAL_STATUS.keys())
    # eac_1
    offerer = next(offerer_iterator)
    create_venue(
        managingOfferer=offerer,
        name=f"reimbursementPoint {offerer.name} 56",
        reimbursement=True,
        adageId="123546",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=3),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        departementCode="56",
        postalCode="56000",
        city="Lorient",
    )
    # eac_2
    offerer = next(offerer_iterator)
    create_venue(
        managingOfferer=offerer,
        name=f"reimbursementPoint {offerer.name} 91",
        adageId="7894896",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=5),
        reimbursement=True,
        siret="12345678200010",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        departementCode="91",
        postalCode="91000",
        city="CORBEIL-ESSONNES",
    )
    create_venue(
        managingOfferer=offerer,
        name=f"real_venue 1 {offerer.name}",
        siret="12345678200036",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
    )
    # eac_pending_bank_informations
    offerer = next(offerer_iterator)
    pending_reimbursement_venue = offerers_factories.VenueFactory(
        managingOfferer=offerer,
        name=f"reimbursementPoint {offerer.name}",
        adageId="789456",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=30),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
    )
    pending_reimbursement_venue.bankInformation = finance_factories.BankInformationFactory(
        status=finance_models.BankInformationStatus.DRAFT
    )
    offerers_factories.VenueReimbursementPointLinkFactory(
        venue=pending_reimbursement_venue,
        reimbursementPoint=pending_reimbursement_venue,
    )
    # eac_no_cb
    offerer = next(offerer_iterator)
    create_venue(
        managingOfferer=offerer,
        name=f"real_venue 1 {offerer.name}",
        adageId="698748",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=13),
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
    )
    # eac_rejected
    offerer = next(offerer_iterator)
    create_venue(
        managingOfferer=offerer,
        name=f"reimbursementPoint {offerer.name}",
        reimbursement=True,
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
    )
    create_venue(
        managingOfferer=offerer,
        name=f"real_venue 1 {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
    )
    # DMS venues
    application_id_generator = count(11922836)
    # eac_accepte
    offerer = next(offerer_iterator)
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret="42883745400050",
    )
    educational_factories.CollectiveDmsApplicationFactory(
        venue=venue,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.fromisoformat("2023-03-26T16:08:35+01:00"),
        depositDate=datetime.fromisoformat("2024-03-23T16:08:33+01:00"),
        expirationDate=datetime.fromisoformat("2025-03-23T16:08:33+01:00"),
        buildDate=datetime.fromisoformat("2023-03-23T16:08:35+01:00"),
        instructionDate=datetime.fromisoformat("2025-03-24T16:08:33+01:00"),
        processingDate=datetime.fromisoformat("2025-03-25T16:08:33+01:00"),
        state="accepte",
    )
    # eac_sans_suite
    offerer = next(offerer_iterator)
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret="42883745400051",
    )
    educational_factories.CollectiveDmsApplicationFactory(
        venue=venue,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.fromisoformat("2023-03-26T16:08:35+01:00"),
        depositDate=datetime.fromisoformat("2024-03-23T16:08:33+01:00"),
        expirationDate=datetime.fromisoformat("2025-03-23T16:08:33+01:00"),
        buildDate=datetime.fromisoformat("2023-03-23T16:08:35+01:00"),
        instructionDate=datetime.fromisoformat("2025-03-24T16:08:33+01:00"),
        processingDate=datetime.fromisoformat("2025-03-25T16:08:33+01:00"),
        state="sans_suite",
    )
    # eac_en_construction
    offerer = next(offerer_iterator)
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret="42883745400052",
    )
    educational_factories.CollectiveDmsApplicationFactory(
        venue=venue,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.fromisoformat("2023-03-26T16:08:35+01:00"),
        depositDate=datetime.fromisoformat("2024-03-23T16:08:33+01:00"),
        expirationDate=datetime.fromisoformat("2025-03-23T16:08:33+01:00"),
        buildDate=datetime.fromisoformat("2023-03-23T16:08:35+01:00"),
        instructionDate=None,
        processingDate=None,
        state="en_construction",
    )
    # eac_refuse
    offerer = next(offerer_iterator)
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret="42883745400053",
    )
    educational_factories.CollectiveDmsApplicationFactory(
        venue=venue,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.fromisoformat("2023-03-26T16:08:35+01:00"),
        depositDate=datetime.fromisoformat("2024-03-23T16:08:33+01:00"),
        expirationDate=datetime.fromisoformat("2025-03-23T16:08:33+01:00"),
        buildDate=datetime.fromisoformat("2023-03-23T16:08:35+01:00"),
        instructionDate=datetime.fromisoformat("2025-03-24T16:08:33+01:00"),
        processingDate=datetime.fromisoformat("2025-03-25T16:08:33+01:00"),
        state="refuse",
    )
    # eac_en_instruction
    offerer = next(offerer_iterator)
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret="42883745400054",
    )
    educational_factories.CollectiveDmsApplicationFactory(
        venue=venue,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.fromisoformat("2023-03-26T16:08:35+01:00"),
        depositDate=datetime.fromisoformat("2024-03-23T16:08:33+01:00"),
        expirationDate=None,
        buildDate=datetime.fromisoformat("2023-03-23T16:08:35+01:00"),
        instructionDate=datetime.fromisoformat("2025-03-24T16:08:33+01:00"),
        processingDate=None,
        state="en_instruction",
    )
    # eac_complete_30+d
    offerer = next(offerer_iterator)
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret="42883745400055",
        adageId="98763",
        adageInscriptionDate=datetime.utcnow() - timedelta(days=30),
    )
    educational_factories.CollectiveDmsApplicationFactory(
        venue=venue,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.fromisoformat("2022-11-08 14:09:33+00:00"),
        depositDate=datetime.fromisoformat("2022-05-17 14:43:22+00:00"),
        expirationDate=datetime.fromisoformat("2025-11-08 14:09:31+00:00"),
        buildDate=datetime.fromisoformat("2022-05-17 14:43:22+00:00"),
        instructionDate=datetime.fromisoformat("2022-10-25 12:40:41+00:00"),
        processingDate=datetime.fromisoformat("2022-11-08 14:09:31+00:00"),
        state="accepte",
    )
    # eac_complete_30-d
    offerer = next(offerer_iterator)
    venue = create_venue(
        managingOfferer=offerer,
        name=f"accepted_dms {offerer.name}",
        venueEducationalStatusId=next(educational_status_iterator),
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        siret="42883745400056",
        adageId="98763",
        adageInscriptionDate=datetime.utcnow(),
    )
    educational_factories.CollectiveDmsApplicationFactory(
        venue=venue,
        application=next(application_id_generator),
        procedure=57189,
        lastChangeDate=datetime.utcnow(),
        depositDate=datetime.fromisoformat("2022-05-17 14:43:22+00:00"),
        expirationDate=datetime.fromisoformat("2025-11-08 14:09:31+00:00"),
        buildDate=datetime.fromisoformat("2022-05-17 14:43:22+00:00"),
        instructionDate=datetime.fromisoformat("2022-10-25 12:40:41+00:00"),
        processingDate=datetime.utcnow(),
        state="accepte",
    )


def create_venue(*, reimbursement: bool = False, **kwargs) -> offerers_models.Venue:  # type: ignore [no-untyped-def]
    venue = offerers_factories.VenueFactory(**kwargs)
    if reimbursement:
        venue.bankInformation = finance_factories.BankInformationFactory()
        offerers_factories.VenueReimbursementPointLinkFactory(
            venue=venue,
            reimbursementPoint=venue,
        )
    return venue


def create_venue_educational_status() -> None:
    for ident, name in VENUE_EDUCATIONAL_STATUS.items():
        offerers_factories.VenueEducationalStatusFactory(id=ident, name=name)
