import pytest
import os
from app import app, db
from models.dog import Dog, AdoptionStatus
from models.breed import Breed


@pytest.fixture
def client():
    """配置测试用 Flask 客户端，使用内存 SQLite 数据库"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.drop_all()
        db.create_all()
        _seed_test_data()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def _seed_test_data():
    """插入测试用品种和狗狗数据"""
    breed1 = Breed(name='Labrador')
    breed2 = Breed(name='Poodle')
    db.session.add_all([breed1, breed2])
    db.session.flush()

    dog1 = Dog(name='Buddy', breed_id=breed1.id, age=3, gender='Male',
               description='A friendly and energetic dog.', status=AdoptionStatus.AVAILABLE)
    dog2 = Dog(name='Bella', breed_id=breed2.id, age=5, gender='Female',
               description='A calm and gentle companion.', status=AdoptionStatus.ADOPTED)
    dog3 = Dog(name='Max', breed_id=breed1.id, age=2, gender='Male',
               description='A playful and loyal friend.', status=AdoptionStatus.PENDING)
    db.session.add_all([dog1, dog2, dog3])
    db.session.commit()


# ---------------------------------------------------------------------------
# GET /api/dogs
# ---------------------------------------------------------------------------

class TestGetDogs:
    def test_returns_200(self, client):
        response = client.get('/api/dogs')
        assert response.status_code == 200

    def test_response_contains_required_keys(self, client):
        data = client.get('/api/dogs').get_json()
        assert 'dogs' in data
        assert 'page' in data
        assert 'per_page' in data
        assert 'total' in data
        assert 'total_pages' in data

    def test_default_pagination(self, client):
        data = client.get('/api/dogs').get_json()
        assert data['page'] == 1
        assert data['per_page'] == 6
        assert data['total'] == 3

    def test_custom_per_page(self, client):
        data = client.get('/api/dogs?per_page=2').get_json()
        assert data['per_page'] == 2
        assert len(data['dogs']) == 2
        assert data['total_pages'] == 2

    def test_page_2(self, client):
        data = client.get('/api/dogs?per_page=2&page=2').get_json()
        assert data['page'] == 2
        assert len(data['dogs']) == 1

    def test_per_page_capped_at_100(self, client):
        data = client.get('/api/dogs?per_page=999').get_json()
        assert data['per_page'] == 100

    def test_page_minimum_is_1(self, client):
        data = client.get('/api/dogs?page=0').get_json()
        assert data['page'] == 1

    def test_dog_item_has_required_fields(self, client):
        dog = client.get('/api/dogs').get_json()['dogs'][0]
        assert 'id' in dog
        assert 'name' in dog
        assert 'breed' in dog

    def test_filter_by_breed(self, client):
        """品种过滤应只返回指定品种的狗"""
        data = client.get('/api/dogs?breed=Labrador').get_json()
        assert len(data['dogs']) == 2  # Buddy and Max
        assert all(dog['breed'] == 'Labrador' for dog in data['dogs'])

    def test_filter_by_available_only(self, client):
        """available=true 过滤应只返回 AVAILABLE 状态的狗"""
        data = client.get('/api/dogs?available=true').get_json()
        assert len(data['dogs']) == 1  # Only Buddy
        assert data['dogs'][0]['name'] == 'Buddy'

    def test_filter_by_breed_and_available(self, client):
        """同时过滤品种和可用性应返回满足两个条件的狗"""
        data = client.get('/api/dogs?breed=Labrador&available=true').get_json()
        assert len(data['dogs']) == 1
        assert data['dogs'][0]['name'] == 'Buddy'
        assert data['dogs'][0]['breed'] == 'Labrador'

    def test_filter_nonexistent_breed(self, client):
        """不存在的品种过滤应返回空列表"""
        data = client.get('/api/dogs?breed=GoldenRetriever').get_json()
        assert len(data['dogs']) == 0
        assert data['total'] == 0


# ---------------------------------------------------------------------------
# GET /api/dogs/<id>
# ---------------------------------------------------------------------------

class TestGetDogById:
    def test_returns_200_for_existing_dog(self, client):
        dog_id = db.session.query(Dog).first().id
        response = client.get(f'/api/dogs/{dog_id}')
        assert response.status_code == 200

    def test_returns_correct_dog(self, client):
        dog_id = db.session.query(Dog).filter_by(name='Buddy').first().id
        data = client.get(f'/api/dogs/{dog_id}').get_json()
        assert data['name'] == 'Buddy'
        assert data['breed'] == 'Labrador'
        assert data['gender'] == 'Male'

    def test_response_has_all_fields(self, client):
        dog_id = db.session.query(Dog).first().id
        data = client.get(f'/api/dogs/{dog_id}').get_json()
        for field in ('id', 'name', 'breed', 'age', 'description', 'gender', 'status'):
            assert field in data

    def test_status_is_string(self, client):
        dog_id = db.session.query(Dog).filter_by(name='Buddy').first().id
        data = client.get(f'/api/dogs/{dog_id}').get_json()
        assert data['status'] == 'AVAILABLE'

    def test_returns_404_for_missing_dog(self, client):
        response = client.get('/api/dogs/99999')
        assert response.status_code == 404

    def test_404_response_has_error_key(self, client):
        data = client.get('/api/dogs/99999').get_json()
        assert 'error' in data


# ---------------------------------------------------------------------------
# GET /api/breeds
# ---------------------------------------------------------------------------

class TestGetBreeds:
    def test_returns_200(self, client):
        response = client.get('/api/breeds')
        assert response.status_code == 200

    def test_response_contains_breeds_key(self, client):
        data = client.get('/api/breeds').get_json()
        assert 'breeds' in data

    def test_returns_all_breeds(self, client):
        data = client.get('/api/breeds').get_json()
        assert len(data['breeds']) == 2

    def test_breed_item_has_id_and_name(self, client):
        breed = client.get('/api/breeds').get_json()['breeds'][0]
        assert 'id' in breed
        assert 'name' in breed

    def test_breed_names_are_correct(self, client):
        names = {b['name'] for b in client.get('/api/breeds').get_json()['breeds']}
        assert names == {'Labrador', 'Poodle'}

    def test_breed_items_ordered_by_id(self, client):
        """品种应按 ID 排序"""
        breeds = client.get('/api/breeds').get_json()['breeds']
        assert breeds[0]['id'] < breeds[1]['id']
