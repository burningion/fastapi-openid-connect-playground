import google.oauth2.credentials
import google_auth_oauthlib.flow

flow = google_auth_oauthlib.flow.Flow.from_client_config('../oauth2_client_secret.json', scopes=[])

