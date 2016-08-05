from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, CatalogItem, Base

engine = create_engine('sqlite:///categorycatalog.db')
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


# Add some categories
for i, cat in enumerate(['city', 'people', 'transport', 'nature']):
    cat_dict = dict()
    cat_dict['name'] = 'Category {}'.format(cat)
    cat_dict['image_loc'] = 'http://lorempixel.com/800/300/{}/{}'.format(
        cat, i+1)
    category = Category(**cat_dict)
    session.add(category)
    session.commit()

# Add some items
for cat in session.query(Category).all():
    for i in range(3):
        item_dict = dict()
        item_dict['name'] = 'Item {}{}'.format(i, cat.id)
        item_dict['description'] = 'This is Item {}'.format(i)
        item_dict['image_loc'] = 'http://lorempixel.com/800/300/{}/{}'.format(
            cat.name[9:], i+1)
        item_dict['category_id'] = cat.id

        item = CatalogItem(**item_dict)
        session.add(item)
        session.commit()
