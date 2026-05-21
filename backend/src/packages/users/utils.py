from .responses import Avatar, AvatarList, Statistics, User, UserList


def cast_user(user: dict) -> User:
    return User(**user)


def cast_statistics(statistics: dict) -> Statistics:
    return Statistics(**statistics)


def cast_users(users: list[dict], total: int) -> UserList:
    return UserList(
        items=[cast_user(u) for u in users],
        total=total,
    )


def cast_avatars(avatars: list[dict], total: int) -> AvatarList:
    return AvatarList(
        items=[Avatar(**a) for a in avatars],
        total=total,
    )
