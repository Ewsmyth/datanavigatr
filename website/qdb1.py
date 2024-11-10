from .models import db  # Import the primary `db` instance

class QDB1(db.Model):  # Bind the model to the qdb1 database
    __bind_key__ = 'qdb1'  # Specify that this model belongs to the 'qdb1' bind
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key for the table
    TX_USER_ID = db.Column(db.String(1000))
    RX_USER_ID = db.Column(db.String(1000))
    TX_ASSOC_USRNM = db.Column(db.String(1000))
    EVENT = db.Column(db.String(1000))
    TX_ASSOC_EMAIL = db.Column(db.String(1000))
    TX_ACCT_PASSWD = db.Column(db.String(1000))
    TX_ACCT_AUTH = db.Column(db.String(1000))
    TX_CTL_BY = db.Column(db.Integer)
    TX_ASSOC_TEAM = db.Column(db.String(1000))
    TX_ASSOC_FNAME = db.Column(db.String(1000))
    TX_ASSOC_LNAME = db.Column(db.String(1000))
    TX_ACCT_STATUS = db.Column(db.String(1000))
    TX_ASSOC_PHONE = db.Column(db.String(1000)) # New
    LOCATION = db.Column(db.String(1000)) # New
    FINANCE_ID = db.Column(db.String(1000)) # New
    CONTENT_ID = db.Column(db.String(1000)) # Changed 
    MEDIA = db.Column(db.String(1000)) # New
    GROUP_PARTICIPANTS = db.Column(db.String(1000))
    GROUP_CHAT_NAME = db.Column(db.String(1000))
    CONTENT = db.Column(db.String(1000))
    UP_TIME = db.Column(db.String(1000))
    INITIAL_TIME = db.Column(db.String(1000))
