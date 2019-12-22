from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()

class Template(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(200), nullable=False)
    url = DB.Column(DB.String(200), nullable=False)
    imgflip_page = DB.Column(DB.String(200), nullable=False)
    filename = DB.Column(DB.String(200))

class Current_Month(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    reddit_id = DB.Column(DB.String(200), nullable=False)
    title = DB.Column(DB.String(200), nullable=False)
    author = DB.Column(DB.String(200), nullable=False)
    media = DB.Column(DB.String(200), nullable=False)
    meme_text = DB.Column(DB.String(200))
    status = DB.Column(DB.String(200))
    timestamp = DB.Column(DB.Integer, nullable=False)
    year = DB.Column(DB.Integer, nullable=False)
    month = DB.Column(DB.Integer, nullable=False)
    day = DB.Column(DB.Integer, nullable=False)
    hour = DB.Column(DB.Integer, nullable=False)
    minute = DB.Column(DB.Integer, nullable=False)
    upvote_ratio = DB.Column(DB.Float, nullable=False)
    upvotes = DB.Column(DB.Integer, nullable=False)
    downvotes = DB.Column(DB.Integer, nullable=False)
    nsfw = DB.Column(DB.String(200))
    num_comments = DB.Column(DB.Integer, nullable=False)

# class Prediction(DB.Model):
#     __tablename__ = 'predictions'
#     __table_args__ = (
#         db.UniqueConstraint('component_id', 'commit_id', name='unique_component_commit'),
#     )

#     id = DB.Column(DB.= DB.Column(DB.Integer, nullable=False) primary_key=True)
#     url = DB.Column(DB.String(200))
#     filename = DB.Column(DB.String(200))
#     hash = DB.Column(DB.String(200), nullable=False)

#     pred = DB.Column(DB.= DB.Column(DB.Integer, nullable=False) DB.ForeignKey('template.name'), nullable=False)
#     template = DB.relationship('Template', backref=DB.backref('preds', lazy=True))