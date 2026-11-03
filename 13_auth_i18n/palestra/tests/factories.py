"""Factory di factory_boy: dati di test validi in una riga, sovrascrivibili campo per campo."""
import factory
from factory.django import DjangoModelFactory

from boards.models import Board, Collaborator, User
from inbox.models import InboundAddress
from places.models import Place


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f'utente{n}@example.com')
    name = factory.Faker('name', locale='it_IT')
    password = factory.PostGenerationMethodCall('set_password', 'password')

    @factory.post_generation
    def salva_password(obj, create, extracted, **kwargs):
        if create:
            obj.save()


class BoardFactory(DjangoModelFactory):
    class Meta:
        model = Board
        skip_postgeneration_save = True

    title = factory.Sequence(lambda n: f'Bacheca {n}')
    description = ''
    owner = factory.SubFactory(UserFactory)

    @factory.post_generation
    def with_places(obj, create, extracted, **kwargs):
        """BoardFactory(with_places=3) crea anche 3 luoghi."""
        if create and extracted:
            PlaceFactory.create_batch(extracted, board=obj)


class CollaboratorFactory(DjangoModelFactory):
    class Meta:
        model = Collaborator

    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)
    role = Collaborator.ROLE_VIEWER


class PlaceFactory(DjangoModelFactory):
    class Meta:
        model = Place

    name = factory.Sequence(lambda n: f'Luogo {n}')
    lat = factory.Faker('pyfloat', min_value=-90, max_value=90)
    lng = factory.Faker('pyfloat', min_value=-180, max_value=180)
    board = factory.SubFactory(BoardFactory)


class InboundAddressFactory(DjangoModelFactory):
    class Meta:
        model = InboundAddress

    board = factory.SubFactory(BoardFactory)