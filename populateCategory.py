#!/usr/bin/python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, CatItem, User

engine = create_engine('sqlite:///categorycatalogwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

adminPic = 'https://pbs.twimg.com/profile_images/'
adminPic += '2671170543/18debd694829ed78203a5a36dd364160_400x400.png'

# Create dummy user
User1 = User(name="Ricky Admin Tham", email="ricky.tham@admin.com",
             picture=adminPic)
session.add(User1)
session.commit()

# Category for Soccer
category1 = Category(name="Soccer")

session.add(category1)
session.commit()

catItem1 = CatItem(user_id=1, name="Ball", description="A soccer ball",
                   category=category1)

session.add(catItem1)
session.commit()


catItem2 = CatItem(user_id=1, name="Soccer Shoes",
                   description="Shoes to play soccer", category=category1)

session.add(catItem2)
session.commit()

catItem3 = CatItem(user_id=1, name="Uniform", description="Soccer Uniform",
                   category=category1)

session.add(catItem2)
session.commit()

catItem4 = CatItem(user_id=1, name="Shin Guards",
                   description="Guards to protect the shin",
                   category=category1)

session.add(catItem4)
session.commit()

# Category for Basketball
category2 = Category(name="Basketball")

session.add(category2)
session.commit()


catItem1 = CatItem(user_id=1, name="Ball", description="A basketball",
                   category=category2)

session.add(catItem1)
session.commit()

catItem2 = CatItem(user_id=1, name="Shoes", description="Basketball shoes",
                   category=category2)

session.add(catItem2)
session.commit()

catItem3 = CatItem(user_id=1, name="Jersey", description="Basketball jersey",
                   category=category2)

session.add(catItem3)
session.commit()

catItem4 = CatItem(user_id=1, name="Rim",
                   description="A random basketball rim", category=category2)

session.add(catItem4)
session.commit()

# Category for Baseball
category3 = Category(name="Baseball")

session.add(category3)
session.commit()

catItem1 = CatItem(user_id=1, name="Bat", description="For batting",
                   category=category3)

session.add(catItem1)
session.commit()

# Category for Frisbee
category4 = Category(name="Frisbee")

session.add(category4)
session.commit()

catItem1 = CatItem(user_id=1, name="Frisbee",
                   description="A disk that is made to throw.",
                   category=category4)

session.add(catItem1)
session.commit()

# Category for Snowboarding
category5 = Category(name="Snowboarding")

session.add(category5)
session.commit()

catItem1 = CatItem(user_id=1, name="Snowboard",
                   description="A board that can ride on snow.",
                   category=category5)

session.add(catItem1)
session.commit()

catItem2 = CatItem(user_id=1, name="Goggles",
                   description="A google for snowboarding.",
                   category=category5)

session.add(catItem2)
session.commit()


# Category for Rock Climbing
category6 = Category(name="Rock Climbing")

session.add(category6)
session.commit()

# Category for Foosball
category7 = Category(name="Foosball")

session.add(category7)
session.commit()

# Category for Skating
category8 = Category(name="Skating")

session.add(category8)
session.commit()

# Category for Hockey
category9 = Category(name="Hockey")

session.add(category9)
session.commit()

catItem1 = CatItem(user_id=1, name="Stick",
                   description="A stick used to wack a disc in Hockey.",
                   category=category9)

session.add(catItem1)
session.commit()

print "added menu items!"
