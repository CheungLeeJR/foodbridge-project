import os
from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from abc import ABC, abstractmethod

db = SQLAlchemy()

# ==========================================
# Task 1: OOP Concepts (High Score Implementation)
# - Abstraction (Abstract mapping method)
# - Encapsulation (Private/Protected variables, properties, setters with validation)
# - Inheritance (Multi-level, Single Table Inheritance in ORM)
# - Polymorphism (Method overriding, Magic methods __lt__, __str__)
# - Design Patterns (Factory Method)
# ==========================================

class AbstractModel(db.Model):
    __abstract__ = True
    
    def display_info(self) -> str:
        """Must be implemented by child classes for Polymorphism."""
        raise NotImplementedError("Subclasses must implement display_info()")



class User(AbstractModel, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    _username = db.Column("username", db.String(80), unique=True, nullable=False)
    __password_hash = db.Column("password_hash", db.String(256), nullable=False) # Strict Private Encapsulation
    _role = db.Column("role", db.String(20), nullable=False) # 'donor' or 'receiver'
    contact_info = db.Column(db.String(200))

    # --- ENCAPSULATION via Properties & Setters ---
    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        self._username = value

    @property
    def role(self):
        return self._role
        
    @role.setter
    def role(self, value):
        if value not in ["donor", "receiver"]:
            raise ValueError("Invalid user role.")
        self._role = value

    def set_password(self, password):
        self.__password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.__password_hash, password)

    # --- POLYMORPHISM & MAGIC METHODS ---
    def display_info(self):
        return f"User [{self.role.capitalize()}]: {self.username}"

    def __str__(self):
        return self.username


class FoodListing(AbstractModel):
    """Base class demonstrating Polymorphic Single-Table Inheritance."""
    __tablename__ = 'food_listing'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50)) # Discriminator for Inheritance
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    expiry_time = db.Column(db.DateTime, nullable=False)
    _status = db.Column("status", db.String(20), default="Available")
    
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    donor = db.relationship('User', foreign_keys=[donor_id])
    
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    receiver = db.relationship('User', foreign_keys=[receiver_id])

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'generic_food'
    }

    @property
    def status(self):
        return self._status

    def claim(self, receiver_id):
        """Encapsulated business logic for claiming food."""
        if self._status == "Available":
            self._status = "Claimed"
            self.receiver_id = receiver_id
            return True
        return False

    def complete_pickup(self):
        if self._status == "Claimed":
            self._status = "Completed"
            return True
        return False

    def display_info(self):
        return f"Food: {self.title} (Status: {self.status})"

    def __lt__(self, other):
        # Magic method allowing sorting lists of FoodListings cleanly using < operator
        return self.expiry_time < other.expiry_time


class PerishableFood(FoodListing):
    """Inheritance: Specific subclass of FoodListing"""
    __mapper_args__ = {'polymorphic_identity': 'perishable'}
    
    def display_info(self):
        return f"⚠️ Perishable: {self.title} (Expires very soon at {self.expiry_time.strftime('%H:%M')})"


class NonPerishableFood(FoodListing):
    """Inheritance: Specific subclass of FoodListing"""
    __mapper_args__ = {'polymorphic_identity': 'non_perishable'}
    
    def display_info(self):
        return f"🥫 Non-Perishable: {self.title} (Long shelf life, expires {self.expiry_time.strftime('%Y-%m-%d')})"


class FoodFactory:
    """Design Pattern: Factory Method to decouple and encapsulate object creation."""
    @staticmethod
    def create_food(food_type, **kwargs):
        if food_type == 'perishable':
            return PerishableFood(**kwargs)
        elif food_type == 'non_perishable':
            return NonPerishableFood(**kwargs)
        else:
            return FoodListing(**kwargs)
