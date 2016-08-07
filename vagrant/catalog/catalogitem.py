"""In this script, some functions have been combined and adapted from:

    - https://github.com/udacity/ud330/blob/master/Lesson4/step2/project.py
    - https://github.com/lobrown/Full-Stack-Foundations
"""


from flask import (Flask, render_template, request, redirect,
                   jsonify, url_for, flash)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc, and_
from database_setup import Base, Category, CatalogItem, User

from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

from forms import FormItem, FormCategory


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog application"

engine = create_engine('sqlite:///categorycatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    """Render the login page"""
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Connection via facebook
    Function retrieved from
    https://github.com/udacity/ud330/blob/master/Lesson4/step2/project.py"""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token'
    url += '?grant_type=fb_exchange_token&client_id='
    url += '%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    # userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals
    # sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture'
    url += '?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<div class="row"> '
    output += '<div class="col-sm-6 col-lg-6 col-md-6">'
    output += '<div class="thumbnail">'
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; height: 100px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    output += '</div> '
    output += '</div> '
    output += '</div> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """Disconnect a user connected via facebook"""
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/'
    url += '%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Connect a user via facebook"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<div class="row"> '
    output += '<div class="col-sm-6 col-lg-6 col-md-6">'
    output += '<div class="thumbnail">'
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; height: 100px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    output += '</div> '
    output += '</div> '
    output += '</div> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


# User Helper Functions

def createUser(login_session):
    """Create a user in the db based on the info stored in the session"""
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Get the user infos from the db given a user id"""
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """Get the user id from the db given an email adress"""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session

@app.route('/gdisconnect')
def gdisconnect():
    """Disconnect a user connected using google"""
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    """Disconnect the user"""
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


@app.route('/category/<string:category_name>/JSON')
def categoryCatalogJSON(category_name):
    """Return a json with all categories and their attributes

    Returns:
        A json of all categories"""
    items = session.query(
        CatalogItem, Category).filter(and_(
            Category.name == category_name,
            CatalogItem.category_id == Category.id)).order_by(
                desc(CatalogItem.date_added)).all()
    return jsonify(CatalogItems=[i.serialize for i, _ in items])


@app.route('/category/all/JSON')
def categoryCatalogJSONall():
    """Return a json with all categories and their attributes

    Returns:
        A json of all categories"""
    items = session.query(CatalogItem).all()
    return jsonify(CatalogItems=[i.serialize for i in items])


@app.route('/category/<string:category_name>/<string:item_name>/JSON')
def catalogItemJSON(category_name, item_name):
    """Return a json with all categories and their attributes

    Returns:
        A json of all categories"""
    # we filter by item name and sort by date added in the db
    item = session.query(
        CatalogItem, Category).filter(and_(
            Category.name == category_name,
            CatalogItem.category_id == Category.id,
            CatalogItem.name == item_name)).order_by(
                desc(CatalogItem.date_added)).one()
    return jsonify(Catalog_Item=item[0].serialize)


@app.route('/category/JSON')
def categoriesJSON():
    """Return a json with all categories and their attributes

    Returns:
        A json of all categories"""
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# Show all categories
@app.route('/')
@app.route('/category/')
def showCategories():
    """Show categories and items

    Render the homepage.

    Returns:
        render the categories template if a GET request is sent"""
    categories = session.query(Category).all()
    items = session.query(
        CatalogItem, Category).filter(
            CatalogItem.category_id == Category.id).order_by(
                desc(CatalogItem.date_added)).all()
    return render_template('categories.html', categories=categories,
                           items=items[:9])


# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    """Create a category

    Need to be logged in to be able to see the edit page.

    Args:
        category_name(str): the name of the category the object belongs to

    Returns:
        render the newCategory template if a GET request is sent
        redirect to the home page if the POST request succeeds"""
    if 'provider' in login_session:
        form = FormCategory()
        if form.validate_on_submit():
            newCategory = Category(name=form.name.data,
                                   image_loc=form.image_loc.data)
            session.add(newCategory)
            session.commit()
            return redirect(url_for('showCategories'))
        return render_template('newCategory.html', form=form)
    else:
        flash("Please login to be able to add a category")
        return redirect(url_for('showCategories'))


@app.route('/category/<string:category_name>/edit/', methods=['GET', 'POST'])
def editCategory(category_name):
    """Edit a category

    Need to be logged in to be able to see the edit page.

    Args:
        category_name(str): the name of the category the object belongs to

    Returns:
        render the editCategory template if a GET request is sent
        redirect to the home page if the POST request succeeds"""
    if 'provider' in login_session:
        editedCategory = session.query(
            Category).filter_by(name=category_name).one()
        form = FormCategory()
        if form.validate_on_submit():
            if len(form.name.data) > 0:
                editedCategory.name = form.name.data
            if len(form.name.data) > 0:
                editedCategory.image_loc = form.image_loc.data
            return redirect(url_for('showCategories'))
        return render_template('editCategory.html',
                               category=editedCategory,
                               form=form)
    else:
        flash("Please login to be able to edit a category")
        return redirect(url_for('showCategories'))


@app.route('/category/<string:category_name>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_name):
    """Delete a category

    Need to be logged in to be able to see the delete page.

    Args:
        category_name(str): the name of the category the object belongs to

    Returns:
        render the deleteCategory template if a GET request is sent
        redirect to the home page if the POST request succeeds"""
    if 'provider' in login_session:
        categoryToDelete = session.query(
            Category).filter_by(name=category_name).one()
        # itemsToDelete = session.query(CatalogItem).filter_by(
        #     category_id=categoryToDelete.id).delete()
        if request.method == 'POST':
            session.delete(categoryToDelete)
            session.commit()
            return redirect(url_for('showCategories'))
        return render_template('deleteCategory.html',
                               category=categoryToDelete)
    else:
        flash("Please login to be able to delete a category")
        return redirect(url_for('showCategories'))


@app.route('/category/<string:category_name>/')
def showCategory(category_name):
    """Show a category and all its items

    Args:
        category_name(str): the name of the category the item belongs to

    Returns:
        render the catalog template"""
    category = session.query(Category).filter_by(name=category_name).one()
    categories = session.query(Category).all()
    items = session.query(CatalogItem).filter_by(
        category_id=category.id).all()
    nb_items = len(items)
    text_item = 'item'
    if nb_items >= 2:
        text_item += 's'
    tuple_items = (nb_items, text_item)
    return render_template('catalog.html', items=items, category=category,
                           categories=categories, tuple_items=tuple_items)


@app.route('/category/<string:category_name>/<string:item_name>')
def showCatalogItem(category_name, item_name):
    """Show an item and all its attributes

    Args:
        category_name(str): the name of the category the item belongs to
        item_name(str): the name of the item

    Returns:
        render the catalogitem template"""
    item = session.query(CatalogItem).filter_by(name=item_name).one()
    category = session.query(Category).filter_by(name=category_name).one()
    return render_template('catalogitem.html', item=item,
                           category=category)


@app.route('/category/<string:category_name>/new/',
           methods=['GET', 'POST'])
def newCatalogItem(category_name):
    """Create a new item in the database

    Args:
        category_name(str): the name of the category the item belongs to

    Returns:
        render the newcatalogitem template if a GET request is sent
        redirect to the category page if the POST request succeeds"""
    if 'provider' in login_session:
        form = FormItem()
        if form.validate_on_submit():
            category = session.query(Category).filter_by(
                name=category_name).one()
            newItem = CatalogItem(name=form.name.data,
                                  description=form.description.data,
                                  category_id=category.id,
                                  image_loc=form.image_loc.data)
            session.add(newItem)
            session.commit()
            return redirect(url_for('showCategory',
                                    category_name=category_name))
        return render_template('newcatalogitem.html',
                               category_name=category_name, form=form)
    else:
        flash("Please login to be able to add a new item")
        return redirect(url_for('showCategory', category_name=category_name))


@app.route('/category/<string:category_name>/<string:item_name>/edit',
           methods=['GET', 'POST'])
def editCatalogItem(category_name, item_name):
    """Edit the attributes of an item in the database

    Args:
        category_name(str): the name of the category the item belongs to
        item_name(str): the name of the item

    Returns:
        render the editcatalogitem template if a GET request is sent
        redirect to the category page if the POST request succeeds"""
    if 'provider' in login_session:
        editedItem = session.query(CatalogItem).filter_by(name=item_name).one()
        form = FormItem()
        if form.validate_on_submit():
            if hasattr(form, 'name'):
                editedItem.name = form.name.data
            if hasattr(form, 'description'):
                editedItem.description = form.description.data
            if hasattr(form, 'image_loc'):
                editedItem.image_loc = form.image_loc.data
            session.add(editedItem)
            session.commit()
            return redirect(url_for('showCategory',
                                    category_name=category_name))
        return render_template('editcatalogitem.html',
                               category_name=category_name,
                               item_name=item_name,
                               item=editedItem,
                               form=form)
    else:
        flash("Please login to be able to edit an item")
        return redirect(url_for('showCategory', category_name=category_name))


@app.route('/category/<string:category_name>/<string:item_name>/delete',
           methods=['GET', 'POST'])
def deleteCatalogItem(category_name, item_name):
    """Deletes an item given a category and an item name
    Need to be logged in to be able to see the delete page.

    Args:
        category_name(str): the name of the category the object belongs to
        item_name(str): the name of the item

    Returns:
        render the deletecatalogitem template if a GET request is sent
        redirect to the category page if the POST request succeeds"""
    if 'provider' in login_session:
        itemToDelete = session.query(CatalogItem).filter_by(
            name=item_name).one()
        if request.method == 'POST':
            session.delete(itemToDelete)
            session.commit()
            return redirect(url_for('showCategory',
                                    category_name=category_name))
        else:
            return render_template('deletecatalogitem.html', item=itemToDelete,
                                   category_name=category_name)
    else:
        flash("Please login to be able to delete an item")
        return redirect(url_for('showCategory', category_name=category_name))


if __name__ == '__main__':
    # app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5000)
