from flask import Response

from tests.resource_test_base import ResourceTestBase


class TestTransformationRequest(ResourceTestBase):

    def test_get_single_request_no_object_store(self, mocker,
                                                mock_rabbit_adaptor):
        import servicex
        mock_transform_request_read = mocker.patch.object(
            servicex.models.TransformRequest,
            'return_request',
            return_value=self._generate_transform_request())
        client = self._test_client(extra_config={'OBJECT_STORE_ENABLED': False},
                                   rabbit_adaptor=mock_rabbit_adaptor)
        response = client.get('/servicex/transformation/1234')
        assert response.status_code == 200
        assert response.json == {'request_id': 'BR549', 'did': '123-456-789',
                                 'columns': 'electron.eta(), muon.pt()',
                                 'selection': None,
                                 'tree-name': "Events",
                                 'image': 'ssl-hep/foo:latest', 'chunk-size': 1000,
                                 'workers': 42, 'result-destination': 'kafka',
                                 'result-format': 'arrow',
                                 'kafka-broker': 'http://ssl-hep.org.kafka:12345',
                                 'workflow-name': None,
                                 'generated-code-cm': None,
                                 'status': "Submitted",
                                 'failure-info': None
                                 }
        mock_transform_request_read.assert_called_with('1234')

    def test_get_single_request_with_object_store(self, mocker, mock_rabbit_adaptor):
        import servicex
        object_store_transform_request = self._generate_transform_request()
        object_store_transform_request.result_destination = 'object-store'
        mock_transform_request_read = mocker.patch.object(
            servicex.models.TransformRequest,
            'return_request',
            return_value=object_store_transform_request)

        local_config = {
            'OBJECT_STORE_ENABLED': True,
            'MINIO_PUBLIC_URL': 'minio.servicex.com:9000',
            'MINIO_ACCESS_KEY': 'miniouser',
            'MINIO_SECRET_KEY': 'leftfoot1'
        }

        client = self._test_client(extra_config=local_config,
                                   rabbit_adaptor=mock_rabbit_adaptor)
        response = client.get('/servicex/transformation/1234')
        assert response.status_code == 200
        print(response.json)
        assert response.json == {'request_id': 'BR549', 'did': '123-456-789',
                                 'columns': 'electron.eta(), muon.pt()',
                                 'selection': None,
                                 'tree-name': "Events",
                                 'image': 'ssl-hep/foo:latest', 'chunk-size': 1000,
                                 'kafka-broker': 'http://ssl-hep.org.kafka:12345',
                                 'workers': 42, 'result-destination': 'object-store',
                                 'result-format': 'arrow',
                                 'minio-access-key': 'miniouser',
                                 'minio-endpoint': 'minio.servicex.com:9000',
                                 'minio-secret-key': 'leftfoot1',
                                 'workflow-name': None,
                                 'generated-code-cm': None,
                                 'status': "Submitted",
                                 'failure-info': None
                                 }

        mock_transform_request_read.assert_called_with('1234')

    def test_get_single_request_to_kafka(self, mocker, mock_rabbit_adaptor):
        import servicex
        kafka_transform_request = self._generate_transform_request()
        kafka_transform_request.result_destination = 'kafka'
        mock_transform_request_read = mocker.patch.object(
            servicex.models.TransformRequest,
            'return_request',
            return_value=kafka_transform_request)

        local_config = {
            'OBJECT_STORE_ENABLED': True,
            'MINIO_PUBLIC_URL': 'minio.servicex.com:9000',
            'MINIO_ACCESS_KEY': 'miniouser',
            'MINIO_SECRET_KEY': 'leftfoot1'
        }

        client = self._test_client(extra_config=local_config,
                                   rabbit_adaptor=mock_rabbit_adaptor)
        response = client.get('/servicex/transformation/1234')
        assert response.status_code == 200
        assert response.json == {'request_id': 'BR549', 'did': '123-456-789',
                                 'columns': 'electron.eta(), muon.pt()',
                                 'selection': None,
                                 'tree-name': "Events",
                                 'image': 'ssl-hep/foo:latest', 'chunk-size': 1000,
                                 'kafka-broker': 'http://ssl-hep.org.kafka:12345',
                                 'workers': 42, 'result-destination': 'kafka',
                                 'result-format': 'arrow',
                                 'workflow-name': None,
                                 'generated-code-cm': None,
                                 'status': "Submitted",
                                 'failure-info': None
                                 }

        mock_transform_request_read.assert_called_with('1234')

    def test_get_single_request_404(self, mocker, mock_rabbit_adaptor):
        import servicex
        mock_transform_request_read = mocker.patch.object(
            servicex.models.TransformRequest, 'return_request',
            return_value=None)
        client = self._test_client(rabbit_adaptor=mock_rabbit_adaptor)
        response = client.get('/servicex/transformation/1234')
        assert response.status_code == 404
        mock_transform_request_read.assert_called_with('1234')

    def test_get_single_request_unauthorized(self, mocker, mock_rabbit_adaptor,
                                             mock_requesting_user,
                                             mock_jwt_required):
        user_id = mock_requesting_user.id
        transform_request = self._generate_transform_request()
        transform_request.submitted_by = user_id + 1
        import servicex
        mock_transform_request_read = mocker.patch.object(
            servicex.models.TransformRequest, 'return_request',
            return_value=transform_request)
        mock_requesting_user.admin = False
        client = self._test_client(rabbit_adaptor=mock_rabbit_adaptor,
                                   extra_config={'ENABLE_AUTH': True})
        response: Response = client.get('/servicex/transformation/1234')
        mock_transform_request_read.assert_called_with('1234')
        assert response.status_code == 401
