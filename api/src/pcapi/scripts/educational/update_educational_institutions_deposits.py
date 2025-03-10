import csv
from datetime import datetime
from decimal import Decimal
import logging
from typing import Iterable

from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.constants import INSTITUTION_TYPES
from pcapi.models import db
from pcapi.repository import repository


logger = logging.getLogger(__name__)

DEFAULT_FILEPATH = "/tmp/"


# Ex: educational_year_beginning = 2021 if educational year is 2021/2022
def update_educational_institutions_deposits(
    filename: str,
    ministry: educational_models.Ministry,
    path: str = DEFAULT_FILEPATH,
    educational_year_beginning: int = None,
) -> None:
    if path is not None and path != DEFAULT_FILEPATH and not path.endswith("/"):
        path += "/"

    with open(f"{path}{filename}", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=";")
        headers = csv_rows.fieldnames
        if not headers or "UAICode" not in headers or "depositAmount" not in headers:
            print("\033[91mERROR: UAICode or depositAmount missing in CSV headers\033[0m")
            return
        _process_educational_csv(csv_rows, ministry, educational_year_beginning)
    return


def _process_educational_csv(
    educational_institutions_rows: Iterable[dict],
    ministry: educational_models.Ministry,
    educational_year_beginning: int = None,
) -> None:
    current_year = educational_year_beginning if educational_year_beginning is not None else datetime.utcnow().year
    try:
        educational_year = educational_repository.get_educational_year_beginning_at_given_year(current_year)
    except exceptions.EducationalYearNotFound:
        print("\033[91mERROR: script has ceased execution")
        print(
            f"Please add educational years in database as no educational year has been found beginning at year {current_year}\033[0m"
        )
        return
    adage_institutions = {
        i.uai: i for i in adage_client.get_adage_educational_institutions(ansco=educational_year.adageId)
    }
    for row in educational_institutions_rows:
        institution_id = row["UAICode"]
        deposit_amount = row["depositAmount"]

        educational_institution = educational_repository.find_educational_institution_by_uai_code(institution_id)
        if educational_institution is None:
            adage_institution = adage_institutions.get(institution_id)
            if adage_institution is None:
                print(
                    f"Educational institution with institution id: {institution_id} is missing. Not found in adage",
                )
                return
            educational_institution = educational_models.EducationalInstitution(
                name=adage_institution.libelle,
                city=adage_institution.communeLibelle,
                postalCode=adage_institution.codePostal,
                email=adage_institution.courriel,
                phoneNumber=adage_institution.telephone or "",
                institutionId=adage_institution.uai,
                institutionType=INSTITUTION_TYPES.get(adage_institution.sigle, ""),
            )
            db.session.add(educational_institution)
            print(
                f"Educational institution with institution id: {institution_id} is missing. We create it with id : {educational_institution.id}",
            )
        educational_deposit = educational_repository.find_educational_deposit_by_institution_id_and_year(
            educational_institution.id, educational_year.adageId
        )
        if not educational_deposit:
            educational_deposit = educational_models.EducationalDeposit(
                educationalYear=educational_year,
                educationalInstitution=educational_institution,
                amount=Decimal(deposit_amount),
                isFinal=True,
                ministry=ministry,
            )
            print("\033[91mERROR: script has ceased execution")
            print(
                f"Deposit for educational institution with id {educational_institution.institutionId} is missing. Please import it first with import_educational_institutions_and_deposits script\033[0m"
            )
            return

        educational_deposit.amount = Decimal(deposit_amount)
        educational_deposit.isFinal = True

        repository.save(educational_deposit)

        logger.info(
            "Educational deposit has been updated",
            extra={
                "educational_deposit_id": educational_deposit.id,
                "script": "import_educational_institutions_and_deposits",
                "amount": str(educational_deposit.amount),
                "uai_code": institution_id,
                "year_id": educational_year.adageId,
            },
        )
