from rest_api_controller import RestApiController
from models import UserModel


"""
Q: Composition over Inherirance  - is it a better way (here) to inherit from RestApiController or to user a RestApiController 
object inside the UserApi class? - I believe Composition is better here 
"""


class UserApi:
    def __init__(self, base_url: str, auth=None) -> None:
        self.controller = RestApiController(base_url, auth)
        self.endpoint = "/users"

    def get_first_page_of_users(self) -> list[dict]:
        return self.controller.get(self.endpoint).json()

    def get_user_id_by_name(self, name: str) -> int:
        """
        This function return the id of the first user with passed name
        """
        users = self.controller.get(self.endpoint, params={"name": name}).json()

        if len(users) <= 0:
            raise ValueError(f"{name} was not found")

        print(
            f"A number of {len(users)} users was found. Only the ID of the first one will be returned"
        )
        return users[0]["id"]

    def get_actual_number_of_users(self) -> int:
        users = self.controller.get(endpoint=self.endpoint)
        no_of_users = int(users.headers.get("x-pagination-total"))
        return no_of_users

    def get_users_by_status(self, number_of_users: int, status: str) -> list[dict]:
        """ "
        This function return a chosen number of user which was the desired status (active/inactive)
        """

        users = self.controller.get(
            self.endpoint,
            params={"status": status, "page": 1, "per_page": number_of_users},
        )
        return users.json()

    def get_users_with_middle_name(self, number_of_users: int) -> list[dict]:
        # users: list[dict] = self.controller.get(endpoint=self.endpoint, params = {"page": page}).json()
        users_with_middle_name:list[dict] = [] 
        page = 1

        while len(users_with_middle_name) < number_of_users:
            response = self.controller.get(endpoint=self.endpoint, params={"page": page, "per_page": 20})
            users: list[dict] = response.json()

            if not users:
                break
            
            for user in users:
                user_name: str = user.get("name")
                if len(user_name.split()) >= 3:
                    users_with_middle_name.append(user)

                if len(users_with_middle_name) == number_of_users:
                    break        
            
            page += 1

        return users_with_middle_name                   

    def add_user(self, user: UserModel, check_if_was_added: bool = False) -> None:
        """
        This function will add a new user
        """
        number_of_users_before = self.get_actual_number_of_users()

        response = self.controller.post(
            endpoint=self.endpoint,
            json={
                "name": user.name,
                "email": user.email,
                "gender": user.gender,
                "status": user.status,
            },
        )

        if response is None:
            print("POST request failed. User was not added")
            return

        if check_if_was_added:
            self.__check_if_user_was_added(number_of_users_before)

        user.update_id(response.json().get("id"))
        print("All good. The new user was added and his/her ID was updated!")

    def change_email_address(self, user_id: str, new_email_address: str) -> None:

        if not self.__check_user_by_id(user_id):
            print("This user does not exist. Please check again.")
            return

        self.controller.put(
            endpoint=self.endpoint + f"/{user_id}",
            json={"email": new_email_address},
        )

        if not self.__check_user_email(id=user_id, email_to_compare=new_email_address):
            print("The email was not changed!")
            return

        print("All good! The email was changed!")

    def __check_user_by_id(self, id: str) -> bool:
        response = self.controller.get(self.endpoint, params={"id": id})

        if len(response.json()) == 0:
            return False

        return True

    def __check_if_user_was_added(self, number_of_users_before: int) -> None:
        number_of_users_after = self.get_actual_number_of_users()
        if number_of_users_after - number_of_users_before == 1:
            print("All good! Total number of users increased by 1!")
        else:
            print("Total number of users DID NOT increased by 1!")

    def __check_user_email(self, email_to_compare: str, id: str) -> bool:
        user = self.controller.get(endpoint=self.endpoint, params={"id": id})

        if user.json()[0].get("email") == email_to_compare:
            return True

        return False
