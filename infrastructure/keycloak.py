from keycloak import KeycloakOpenID, KeycloakAdmin


class Keycloak:
    def __init__(
        self,
        server: str,
        realm: str,
        client_id: str,
        client_secret: str,
        username: str,
        password: str
    ):
        self.cli_openid = KeycloakOpenID(
            server_url=server,
            client_id=client_id,
            client_secret_key=client_secret,
            realm_name=realm
        )
        self.cli_admin = KeycloakAdmin(
            server_url=server,
            username=username,
            password=password,
            realm_name=realm,
            verify=True,
            auto_refresh_token=['get', 'post', 'put', 'delete']
        )
