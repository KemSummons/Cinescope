BASE_URL = "https://restful-booker.herokuapp.com"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

CREATE_TOKEN_ENDPOINT = '/auth' # POST
CREATE_BOOKING_ENDPOINT = '/booking' # POST
GET_BOOKING_IDS_ENDPOINT = '/booking' # GET
GET_BOOKING_ID_ENDPOINT = '/booking/{id}' # GET + ID
UPDATE_BOOKING_ENDPOINT = '/booking/{id}' # PUT + ID
PARTIAL_UPDATE_BOOKING_ENDPOINT = '/booking/{id}' # PATCH + ID
DELETE_BOOKING_ENDPOINT = '/booking/{id}' # DELETE + ID
