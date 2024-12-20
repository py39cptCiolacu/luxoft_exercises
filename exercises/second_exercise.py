from constants import COMMON_URL
from models import UserModel
from apis.user_api import UserApi


def second_exercise() -> None:
    user_api = UserApi(COMMON_URL)

    random_user = UserModel.model_without_id(
        name="Random User", email="email33@email.ro", gender="male", status="inactive"
    )

    user_api.add_user(random_user)
    print(random_user) 