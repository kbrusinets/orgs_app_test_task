from typing import Set

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from geoalchemy2 import Geography


class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = 'organization'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address_id: Mapped[int] = mapped_column(Integer, ForeignKey('address.id'))

    categories: Mapped[Set['Category']] = relationship(secondary='organization_category', back_populates='organizations')
    address: Mapped['Address'] = relationship(back_populates='organizations')


class PhoneNumber(Base):
    __tablename__ = 'phone_number'

    number: Mapped[str] = mapped_column(String, primary_key=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey('organization.id'), nullable=False)


class Address(Base):
    __tablename__ = 'address'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    coordinates: Mapped[str] = mapped_column(Geography(geometry_type='POINT', srid=4326), unique=True)
    country: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    street: Mapped[str] = mapped_column(String)
    home: Mapped[str] = mapped_column(String)

    organizations: Mapped[Set['Organization']] = relationship(back_populates='address')


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_id: Mapped[int] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String)

    organizations: Mapped[Set['Organization']] = relationship(secondary='organization_category', back_populates='categories')


class OrganizationCategory(Base):
    __tablename__ = 'organization_category'

    org_id: Mapped[int] = mapped_column(Integer, ForeignKey('organization.id'), primary_key=True)
    cat_id: Mapped[int] = mapped_column(Integer, ForeignKey('category.id'), primary_key=True)
