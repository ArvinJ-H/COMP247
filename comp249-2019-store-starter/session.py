"""
Code for handling sessions in our web application
"""

from bottle import request, response
import uuid
import json

import model
import dbschema

COOKIE_NAME = 'session'


def get_or_create_session(db):
    """Get the current sessionid either from a
    cookie in the current request or by creating a
    new session if none are present.

    If a new session is created, a cookie is set in the response.

    Returns the session key (string)
    """

    key = request.get_cookie(COOKIE_NAME)

    cur = db.cursor()
    cur.execute("SELECT sessionid FROM sessions WHERE sessionid=?", (key,))

    row = cur.fetchone()

    if not row:
        key = str(uuid.uuid4())

        sql = "INSERT INTO sessions (sessionid) VALUES (?)"
        cursor = db.cursor()
        cursor.execute(sql, [key])
        db.commit()
        # set the corrent cookie
        response.set_cookie(COOKIE_NAME, key)

    return key


# also a list
cartlist = []


def add_to_cart(db, itemid, quantity):
    """Add an item to the shopping cart"""

    sessionid = get_or_create_session(db)
    cur = db.cursor()
    cur.execute(
        "SELECT sessionid FROM sessions WHERE sessionid = ?", (sessionid,))
    item = model.product_get(db, itemid)
# values
    cartlist.append({
        'id': itemid,
        'quantity': quantity,
        'name': item[1],
        'cost': item[6]*quantity #calcu the cost
    })

    data = json.dumps(cartlist)
    cur.execute("UPDATE sessions SET data = ? WHERE sessionid = ?",
                (data, sessionid))
    db.commit()


def get_cart_contents(db):
    """Return the contents of the shopping cart as
    a list of dictionaries:
    [{'id': <id>, 'quantity': <qty>, 'name': <name>, 'cost': <cost>}, ...]
    """

    cur = db.cursor()
    cur.execute("SELECT data FROM sessions WHERE sessionid = ?",
                (get_or_create_session(db),))
    list = cur.fetchone()

    if list['data'] is None:
        return []

    return json.loads(list['data'])


