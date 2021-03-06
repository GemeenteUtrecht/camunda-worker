from django.test import TestCase

import requests_mock
from django_camunda.utils import serialize_variable
from zgw_consumers.test import mock_service_oas_get

from bptl.camunda.models import ExternalTask
from bptl.tasks.tests.factories import DefaultServiceFactory, TaskMappingFactory

from ..tasks import CreateZaakTask

ZTC_URL = "https://some.ztc.nl/api/v1/"
ZRC_URL = "https://some.zrc.nl/api/v1/"
ZAAKTYPE = f"{ZTC_URL}zaaktypen/abcd"
STATUSTYPE = f"{ZTC_URL}statustypen/7ff0bd9d-571f-47d0-8205-77ae41c3fc0b"
ROLTYPE_URL = f"{ZTC_URL}roltypen"
ZAAK = f"{ZRC_URL}zaken/4f8b4811-5d7e-4e9b-8201-b35f5101f891"
STATUS = f"{ZRC_URL}statussen/b7218c76-7478-41e9-a088-54d2f914a713"
ROLTYPE = f"{ZTC_URL}roltypen/64dae7f9-8d11-4b11-9a10-747acb73630e"

RESPONSES = {
    ZAAK: {
        "url": ZAAK,
        "uuid": "4f8b4811-5d7e-4e9b-8201-b35f5101f891",
        "identificatie": "ZAAK-2020-0000000013",
        "bronorganisatie": "002220647",
        "omschrijving": "",
        "zaaktype": ZAAKTYPE,
        "registratiedatum": "2020-01-16",
        "verantwoordelijkeOrganisatie": "002220647",
        "startdatum": "2020-01-16",
        "einddatum": None,
    },
}


def mock_statustypen_get(m):
    m.get(
        f"{ZTC_URL}statustypen?zaaktype={ZAAKTYPE}",
        json={
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "url": STATUSTYPE,
                    "omschrijving": "initial",
                    "zaaktype": ZAAKTYPE,
                    "volgnummer": 1,
                    "isEindstatus": False,
                    "informeren": False,
                },
            ],
        },
    )


def mock_status_post(m):
    m.post(
        f"{ZRC_URL}statussen",
        status_code=201,
        json={
            "url": STATUS,
            "uuid": "b7218c76-7478-41e9-a088-54d2f914a713",
            "zaak": ZAAK,
            "statustype": STATUSTYPE,
            "datumStatusGezet": "2020-01-16T00:00:00.000000Z",
            "statustoelichting": "",
        },
    )


def mock_roltype_get(m):
    m.get(
        f"{ROLTYPE_URL}?zaaktype={ZAAKTYPE}&omschrijvingGeneriek=initiator",
        json={
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "url": ROLTYPE,
                    "omschrijving": "roltype omschrijving",
                    "zaaktype": ZAAKTYPE,
                    "omschrijvingGeneriek": "initiator",
                },
            ],
        },
    )


def mock_rol_post(m):
    m.post(
        f"{ZRC_URL}rollen",
        status_code=201,
        json={
            "zaak": ZAAK,
            "betrokkene": "",
            "betrokkeneType": "natuurlijk_persoon",
            "roltype": ROLTYPE,
            "roltoelichting": "A test roltoelichting",
            "indicatieMachtiging": "",
            "betrokkeneIdentificatie": {},
        },
    )


@requests_mock.Mocker()
class CreateZaakTaskTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        mapping = TaskMappingFactory.create(topic_name="some-topic")
        DefaultServiceFactory.create(
            task_mapping=mapping,
            service__api_root=ZRC_URL,
            service__api_type="zrc",
            alias="ZRC",
        )
        DefaultServiceFactory.create(
            task_mapping=mapping,
            service__api_root=ZTC_URL,
            service__api_type="ztc",
            alias="ZTC",
        )
        cls.fetched_task = ExternalTask.objects.create(
            topic_name="some-topic",
            worker_id="test-worker-id",
            task_id="test-task-id",
            variables={
                "zaaktype": serialize_variable(ZAAKTYPE),
                "organisatieRSIN": serialize_variable("002220647"),
                "NLXProcessId": serialize_variable("12345"),
                "services": serialize_variable(
                    {
                        "ZRC": {"jwt": "Bearer 12345"},
                        "ZTC": {"jwt": "Bearer 789"},
                    }
                ),
            },
        )

    def test_create_zaak(self, m):
        mock_service_oas_get(m, ZTC_URL, "ztc")
        mock_service_oas_get(m, ZRC_URL, "zrc")

        mock_statustypen_get(m)
        m.post(f"{ZRC_URL}zaken", status_code=201, json=RESPONSES[ZAAK])
        mock_status_post(m)

        task = CreateZaakTask(self.fetched_task)

        result = task.perform()
        self.assertEqual(
            result,
            {
                "zaakUrl": ZAAK,
                "zaakIdentificatie": "ZAAK-2020-0000000013",
            },
        )

        request_zaak = next(
            filter(
                lambda x: x.url == f"{ZRC_URL}zaken" and x.method == "POST",
                m.request_history,
            )
        )
        self.assertEqual(request_zaak.headers["X-NLX-Request-Process-Id"], "12345")
        self.assertEqual(request_zaak.headers["Authorization"], "Bearer 12345")

    def test_extra_variables(self, m):
        self.fetched_task.variables["zaakDetails"] = serialize_variable(
            {
                "omschrijving": "foo",
            }
        )
        self.fetched_task.save(0)

        mock_service_oas_get(m, ZTC_URL, "ztc")
        mock_service_oas_get(m, ZRC_URL, "zrc")

        mock_statustypen_get(m)
        response = RESPONSES[ZAAK].copy()
        response["omschrijving"] = "foo"
        m.post(f"{ZRC_URL}zaken", status_code=201, json=response)
        mock_status_post(m)
        task = CreateZaakTask(self.fetched_task)

        task.perform()

        request_zaak = next(
            filter(
                lambda x: x.url == f"{ZRC_URL}zaken" and x.method == "POST",
                m.request_history,
            )
        )

        self.assertEqual(request_zaak.json()["omschrijving"], "foo")

    def test_create_zaak_with_rol(self, m):
        mock_service_oas_get(m, ZTC_URL, "ztc")
        mock_service_oas_get(m, ZRC_URL, "zrc")

        mock_statustypen_get(m)
        m.post(f"{ZRC_URL}zaken", status_code=201, json=RESPONSES[ZAAK])
        mock_status_post(m)

        mock_roltype_get(m)
        mock_rol_post(m)

        task_with_initiator = ExternalTask.objects.create(
            topic_name="some-topic",
            worker_id="test-worker-id",
            task_id="test-task-id",
            variables={
                "zaaktype": serialize_variable(ZAAKTYPE),
                "organisatieRSIN": serialize_variable("002220647"),
                "NLXProcessId": serialize_variable("12345"),
                "services": serialize_variable(
                    {
                        "ZRC": {"jwt": "Bearer 12345"},
                        "ZTC": {"jwt": "Bearer 789"},
                    }
                ),
                "initiator": serialize_variable(
                    {
                        "betrokkeneType": "natuurlijk_persoon",
                        "roltoelichting": "A test roltoelichting",
                    }
                ),
            },
        )

        task = CreateZaakTask(task_with_initiator)
        result = task.perform()

        self.assertEqual(
            result,
            {
                "zaakUrl": ZAAK,
                "zaakIdentificatie": "ZAAK-2020-0000000013",
            },
        )
        # check that the /api/v1/rollen endpoint was called correctly
        self.assertEqual(m.last_request.url, "https://some.zrc.nl/api/v1/rollen")
        self.assertIsInstance(m.last_request.json(), dict)
