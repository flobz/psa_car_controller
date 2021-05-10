from mylogger import logger
from psa_connectedcar import Position, Geometry, PositionProperties, Kinetic, Energy, EnergyCharging, Status


# pylint: disable=too-many-arguments
class CarStatus(Status):
    def __init__(self, embedded=None, links=None, battery=None, doors_state=None, energy=None, environment=None,
                 ignition=None, kinetic=None, last_position=None, preconditionning=None, privacy=None, safety=None,
                 service=None, timed_odometer=None):  # noqa: E501
        super().__init__(embedded, links, battery, doors_state, energy, environment, ignition, kinetic, last_position,
                         preconditionning, privacy, safety, service, timed_odometer)
        self.correct()

    def correct(self):
        try:
            if len(self.last_position.geometry.coordinates) < 2:
                raise AttributeError()
            if len(self.last_position.geometry.coordinates) < 3:
                # set altitude none
                self.last_position.geometry.coordinates.append(None)
        except AttributeError:
            self.last_position = Position(geometry=Geometry(coordinates=[None, None, None], type="Point"),
                                          properties=PositionProperties(updated_at=None))
        if self.kinetic is None:
            self.kinetic = Kinetic()
        # always put electric energy first
        if len(self._energy) == 2 and self._energy[0].type != 'Electric':
            self._energy = self._energy[::-1]

    def is_moving(self):
        try:
            return self.kinetic.moving
        except AttributeError:
            logger.error("kinetic not available from api")
            return None

    def get_energy(self, energy_type) -> Energy:
        for energy in self._energy:
            if energy.type == energy_type:
                return energy
        return Energy(charging=EnergyCharging())
