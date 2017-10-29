from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_db import Base, Sport, CategoryItem, User
from datetime import datetime
import re

engine = create_engine('sqlite:///itemscatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def add_to(d):
    session.add(d)
    session.commit()
    print 'added ', str(d)


def current_date():
    new_date = re.sub(r'-', "", str(datetime.now()))
    new_date = re.sub(r':', "", new_date)
    new_date = re.sub(r' ', "", new_date)
    new_date = float(new_date)
    return new_date

current_date = current_date()
print current_date

# Create dummy user
User1 = User(name="Mike", email="mchanudacity@gmail.com")
add_to(User1)

User2 = User(name="Tim", email="tim@udacity.com")
add_to(User2)


# Add Sports
sport1 = Sport(user_id=1, name="Soccer")
add_to(sport1)

sport2 = Sport(user_id=1, name="Hockey")
add_to(sport2)

sport3 = Sport(user_id=1, name="Football")
add_to(sport3)

# Add Soccer items

soccer_item_1 = CategoryItem(user_id=1, title="Soccer Ball",
                             description="Ball to play soccer",
                             price="$30", category="Ball", sport=sport1,
                             date=current_date)
add_to(soccer_item_1)

soccer_item_2 = CategoryItem(user_id=1, title="Soccer cleats",
                             description="Shoes to wear to play soccer",
                             price="$7.50", category="Shoe", sport=sport1,
                             date=current_date)
add_to(soccer_item_2)

soccer_item_3 = CategoryItem(user_id=1, title="Soccer Jersey",
                             description="Jersey to wear to play soccer",
                             price="$20", category="Shirt", sport=sport1,
                             date=current_date)
add_to(soccer_item_3)

# Add Hockey items...

hockey_item_1 = CategoryItem(user_id=1, title="Hockey Puck",
                             description="Puck to play hockey and score with",
                             price="$7.50", category="Ball", sport=sport2,
                             date=current_date)
add_to(hockey_item_1)

hockey_item_2 = CategoryItem(user_id=1, title="Hockey Skate Shoes",
                             description="Ball to play soccer",
                             price="$30", category="Shoe", sport=sport2,
                             date=current_date)
add_to(hockey_item_2)

hockey_item_3 = CategoryItem(user_id=1, title="Hockey Jersey",
                             description="Jersey to play hockey",
                             price="$40", category="Shirt", sport=sport2,
                             date=current_date)
add_to(hockey_item_3)

# Add Football items...
football_item_1 = CategoryItem(user_id=1, title="Football ball",
                               description="Ball to play football with and " +
                                           "make touchdowns",
                               price="$15", category="Ball", sport=sport3,
                               date=current_date)
add_to(football_item_1)

football_item_2 = CategoryItem(user_id=1, title="Football Torso Pads",
                               description="To protect your body with" +
                                           "when tackled.",
                               price="$30", category="Shoe", sport=sport3,
                               date=current_date)
add_to(football_item_2)

football_item_3 = CategoryItem(user_id=1, title="Football Jersey",
                               description="Jersey to play football.",
                               price="$35", category="Shirt", sport=sport3,
                               date=current_date)
add_to(football_item_3)

print "added menu items!"
