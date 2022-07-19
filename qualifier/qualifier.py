import typing
from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    scope: typing.Mapping[str, typing.Any]

    receive: typing.Callable[[], typing.Awaitable[object]]
    send: typing.Callable[[object], typing.Awaitable[None]]


class RestaurantManager:
    def __init__(self):
        """Instantiate the restaurant manager.

        This is called at the start of each day before any staff get on
        duty or any orders come in. You should do any setup necessary
        to get the system working before the day starts here; we have
        already defined a staff dictionary.
        """
        self.staff = {}

    async def __call__(self, request: Request):
        """Handle a request received.

        This is called for each request received by your application.
        In here is where most of the code for your system should go.

        :param request: request object
            Request object containing information about the sent
            request to your application.
        """

        if request.scope['type'] == 'staff.onduty':
            self.staff[request.scope['id']] = request
        elif request.scope['type'] == 'staff.offduty':
            self.staff.pop(request.scope['id'])
        elif request.scope['type'] == 'order':
            full_order = await request.receive()
            found = self.__find_staff_member(request.scope['speciality'])
            await found.send(full_order)
            result = await found.receive()
            await request.send(result)
            # add staff member back to roster once done
            self.staff[found.scope['id']] = found
        else:
            raise Exception('Unknown request type')

    def __find_staff_member(self, speciality) -> Request:
        """Get the next available staff member, preferably one for speciality.

        :speciality: speciality of the next order
        """

        for key, staff_member in self.staff.copy().items():
            if speciality in staff_member.scope['speciality']:
                self.staff.pop(key)
                return staff_member

        # If no staff for specialty is found, get first staff member from dict
        return self.staff.pop(next(iter(self.staff)))
