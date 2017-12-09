# CTIS API
This is the documentation for the API of CTIS - CU Travel Information System.
The API is built on Flask - A Python web framework.

## Key Notes
- Drivers register and come 'online' when they are driving.
- Drivers are tracked using their browser coordinates.
- Bus-stop locations are stored using the admin, and are displayed on the map.
- The user (driver) is the center of the implementation, as it's his/her phone that's being used. If a driver is deleted,
the shuttle would have to be deleted too.
- All this information is displayed on a map, showing the drivers and locations.
- Users can then get to know, based on their current location or a selected bus-stop, when the next shuttle would arrive.

##Long term extra features
- Add the locations of all the buildings to the map, so people can navigate on foot like Waze.

