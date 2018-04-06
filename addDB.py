from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Category, Item, Base

engine = create_engine('sqlite:////var/www/ItemCatalog/ItemCatalog/main.db')
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

# Category/Item Setup
category1 = Category(name="Chinese Cuisine")
session.add(category1)
session.commit()

categoryItem1 = Item(
    name="Soup Dumplings",
    description="Xiaolongbao is a type of Chinese steamed bun (baozi) from the\
     Jiangnan region, especially associated with Shanghai and Wuxi. It is \
    traditionally prepared in xiaolong, small bamboo steaming baskets, \
    which give them their name. Xiaolongbao are often referred to as a kind of\
     ""dumpling"", but should not be confused with British or American-style\
      dumplings, nor with Chinese jiaozi. Similarly, they are considered a\
       kind of ""soup dumpling"" but should not be confused with other \
       larger varieties of tang bao. In Shanghainese, they are also sometimes\
        known as siaulon moedeu or xiaolong-style mantous",
    category=category1
    )
session.add(categoryItem1)
session.commit()

categoryItem2 = Item(
    name="Lo Mein",
    description="Lo mein is a Chinese dish with wheat flour noodles. It often\
     contains vegetables and some type of meat or seafood, usually beef,\
      chicken, pork, shrimp or wontons. It can also be eaten with just\
       vegetables.",
    category=category1
    )
session.add(categoryItem2)
session.commit()

category2 = Category(name="Spanish Cuisine")
session.add(category2)
session.commit()

categoryItem1 = Item(
    name="Paella",
    description="Originating in Valencia, paella is a rice dish prepared\
     with seafood. Of all the foods in Spain, this is the most popular.\
          In this dish, savory yellow rice is combined with tomatoes,\
           onions, peas, shellfish, squid, clams and chicken drumsticks.",
    category=category2
    )
session.add(categoryItem1)
session.commit()

categoryItem2 = Item(
    name="Gazpacho",
    description="Andalusian Gazpacho is a cold soup made of raw blended\
     vegetables. A classic of Spanish cuisine, it originating in the\
      southern region of Andalusia. Gazpacho is widely eaten in Spain\
       and Portugal, particularly during the hot summers, as it is\
        refreshing and cool.",
    category=category2
    )
session.add(categoryItem2)
session.commit()

category3 = Category(name="French Cuisine")
session.add(category3)
session.commit()

categoryItem1 = Item(
    name="Escargot",
    description="Escargots are popular in Spain and Portugal, but are\
     perhaps most known as a part of French cuisine. This escargot\
      recipe calls for canned snails, so there's no need to hunt down\
       any fresh ones, and makes for a sophisticated appetizer at any\
        dinner party.",
    category=category3
    )
session.add(categoryItem1)
session.commit()

categoryItem2 = Item(
    name="Duck Confit",
    description="Duck confit is a French dish made with the whole duck.\
     In Gascony, according to the families perpetuating the tradition of\
      duck confit, all the pieces of duck are used to produce the meal.\
       Each part can have a specific destination in traditional cooking,\
        the neck being used for example in an invigorating soup,\
         the garbure.",
    category=category3
    )
session.add(categoryItem2)
session.commit()

category4 = Category(name="Italian Cuisine")
session.add(category4)
session.commit()

categoryItem1 = Item(
    name="Campania",
    description="Campania extensively produces tomatoes, peppers,\
     spring onions, potatoes, artichokes, fennel, lemons and oranges\
      which all take on the flavor of volcanic soil. The Gulf of Naples\
       offers fish and seafood. Campania is one of the largest producers\
        and consumers of pasta in Italy, especially spaghetti. In the\
         regional cuisine, pasta is prepared in various styles that can\
          feature tomato sauce, cheese, clams and shellfish.",
    category=category4
    )
session.add(categoryItem1)
session.commit()

categoryItem2 = Item(
    name="Risotto",
    description="A northern Italian rice dish cooked in a broth to a\
     creamy consistency. The broth can be derived from meat, fish, or\
      vegetables. Many types of risotto contain butter, wine, and onion.\
       It is one of the most common ways of cooking rice in Italy. Saffron\
        was originally used for flavour and its attractive yellow colour.",
    category=category4
    )
session.add(categoryItem2)
session.commit()

print "DB Updated!"

