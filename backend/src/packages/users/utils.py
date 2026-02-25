from .responses import Avatar, AvatarList, User, UserList, Statistics
from utils.cast import create_caster


cast_user = create_caster(User)
cast_avatar = create_caster(Avatar)
cast_statistics = create_caster(Statistics)


def cast_users(users: list[dict], total: int) -> UserList:
    return UserList(
        items=[cast_user(user) for user in users],
        total=total,
    )


def cast_avatars(avatars: list[dict], total: int) -> AvatarList:
    return AvatarList(
        items=[cast_avatar(avatar) for avatar in avatars],
        total=total,
    )
