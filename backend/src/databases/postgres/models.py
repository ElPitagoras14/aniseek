from sqlalchemy import (
    Column,
    DateTime,
    String,
    Integer,
    Boolean,
    Text,
    ForeignKey,
    TIMESTAMP,
    CheckConstraint,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid

Base = declarative_base()


class Franchise(Base):
    __tablename__ = "franchises"

    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)

    animes = relationship(
        "Anime", back_populates="franchise", cascade="all, delete"
    )


class AnimeRelation(Base):
    __tablename__ = "anime_relations"

    anime_id = Column(
        String(255),
        ForeignKey("animes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    related_anime_id = Column(
        String(255),
        ForeignKey("animes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    type_related_id = Column(
        Integer,
        ForeignKey("related_types.id", ondelete="CASCADE"),
        primary_key=True,
    )

    __table_args__ = (
        CheckConstraint(
            "anime_id <> related_anime_id", name="chk_not_self_relation"
        ),
    )

    anime = relationship(
        "Anime", foreign_keys=[anime_id], back_populates="relations"
    )
    related_anime = relationship(
        "Anime", foreign_keys=[related_anime_id], lazy="selectin"
    )
    type_related = relationship("RelatedType", lazy="selectin")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Anime(Base):
    __tablename__ = "animes"

    id = Column(String(255), primary_key=True)
    franchise_id = Column(
        String(255),
        ForeignKey("franchises.id", ondelete="SET NULL"),
        nullable=True,
    )
    season = Column(Integer, default=1)
    title = Column(String(255))
    description = Column(Text)
    poster = Column(Text)
    type = Column(String(255))
    is_finished = Column(Boolean)
    week_day = Column(Text)
    last_scraped_at = Column(DateTime(timezone=True))
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    genres = relationship(
        "Genre", back_populates="anime", cascade="all, delete"
    )
    episodes = relationship(
        "Episode", back_populates="anime", cascade="all, delete"
    )
    franchise = relationship("Franchise", back_populates="animes", cascade="")
    relations = relationship(
        "AnimeRelation",
        back_populates="anime",
        foreign_keys="[AnimeRelation.anime_id]",
        lazy="selectin",
    )
    saves = relationship(
        "UserSaveAnime", back_populates="anime", cascade="all, delete"
    )


class Genre(Base):
    __tablename__ = "genres"

    anime_id = Column(
        String(255),
        ForeignKey("animes.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    name = Column(String(255), primary_key=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    anime = relationship("Anime", back_populates="genres")


class RelatedType(Base):
    __tablename__ = "related_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    anime_id = Column(
        String(255),
        ForeignKey("animes.id", ondelete="CASCADE"),
        nullable=False,
    )
    ep_number = Column(Integer, nullable=False)
    url = Column(Text, nullable=False)
    preview = Column(Text)
    job_id = Column(String)
    status = Column(String)
    size = Column(Integer)
    created_at = Column(String, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(String, server_default="CURRENT_TIMESTAMP")

    __table_args__ = (
        UniqueConstraint(
            "anime_id", "ep_number", name="uq_episode_anime_number"
        ),
    )

    anime = relationship("Anime", back_populates="episodes")
    downloads = relationship(
        "UserDownloadEpisode", back_populates="episode", cascade="all, delete"
    )


class RoleType(Base):
    __tablename__ = "role_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Avatar(Base):
    __tablename__ = "avatars"

    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="avatar")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(64), unique=True, nullable=False)
    password = Column(String(60), nullable=False)
    avatar_id = Column(
        Integer, ForeignKey("avatars.id", ondelete="SET NULL"), nullable=True
    )
    role_id = Column(
        Integer,
        ForeignKey("role_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    saves = relationship(
        "UserSaveAnime", back_populates="user", cascade="all, delete"
    )
    downloads = relationship(
        "UserDownloadEpisode", back_populates="user", cascade="all, delete"
    )
    role = relationship("RoleType")
    api_keys = relationship(
        "ApiKey", back_populates="user", cascade="all, delete"
    )
    avatar = relationship("Avatar", back_populates="users", lazy="joined")


class UserSaveAnime(Base):
    __tablename__ = "user_save_anime"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    anime_id = Column(
        String(255),
        ForeignKey("animes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="saves")
    anime = relationship("Anime", back_populates="saves")


class UserDownloadEpisode(Base):
    __tablename__ = "user_download_episode"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    episode_id = Column(
        Integer,
        ForeignKey("episodes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="downloads")
    episode = relationship("Episode", back_populates="downloads")


class ApiScope(Base):
    __tablename__ = "api_scopes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    key = Column(String(255), unique=True, nullable=False)
    expired_at = Column(DateTime(timezone=True))
    last_used_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="api_keys")
