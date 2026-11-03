"""Factory di factory_boy (livello 11).

TODO (passo 2): sostituisci i segnaposto con classi factory.django.DjangoModelFactory:
  - UserFactory: email unica (factory.Sequence), name, password 'password'
    (PostGenerationMethodCall('set_password', 'password'))
  - BoardFactory: title, owner = SubFactory(UserFactory); hook post_generation
    with_places: BoardFactory(with_places=3) crea anche 3 luoghi
  - CollaboratorFactory: board e user con SubFactory, ruolo viewer
  - PlaceFactory: name, lat in [-90, 90], lng in [-180, 180], board = SubFactory
  - InboundAddressFactory: board = SubFactory (il token lo genera il modello)
"""


class _DaFare:
    """Segnaposto: ogni uso dice quale passo manca."""

    def __new__(cls, *args, **kwargs):
        raise NotImplementedError(f'TODO passo 2: {cls.__name__}')

    @classmethod
    def build(cls, *args, **kwargs):
        raise NotImplementedError(f'TODO passo 2: {cls.__name__}.build')

    @classmethod
    def create(cls, *args, **kwargs):
        raise NotImplementedError(f'TODO passo 2: {cls.__name__}.create')

    @classmethod
    def create_batch(cls, *args, **kwargs):
        raise NotImplementedError(f'TODO passo 2: {cls.__name__}.create_batch')


class UserFactory(_DaFare):
    pass


class BoardFactory(_DaFare):
    pass


class CollaboratorFactory(_DaFare):
    pass


class PlaceFactory(_DaFare):
    pass


class InboundAddressFactory(_DaFare):
    pass