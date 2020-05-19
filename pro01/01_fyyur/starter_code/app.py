#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import config
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres= db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(500))
    seeking_talent= db.Column(db.Boolean)
    seeking_description = db.Column(db.Text)
    artists = db.relationship('Artist', secondary='shows',backref=db.backref('Venues', lazy=True))

    #def __repr__(self):
    #    return f'id: {self.id}, name: {self.name}, phone:{self.phone}'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.Text)


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'shows'

    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    artist_id= db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    start_time= db.Column(db.DateTime)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format,  locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  areas= Venue.query.order_by(Venue.state, Venue.city).all()
  data=[]
  ven=[]
  city_loop_group= ''
  state_loop_group=''
  count=0
  for area in areas:
      if area.city == city_loop_group and area.state == state_loop_group:
          ven.append({'id':area.id,'name':area.name})
      else:
          if count == 0:
              city_loop_group = area.city
              state_loop_group=area.state
              ven.append({'id':area.id,'name':area.name})
              count=1
              if len(areas)==1:
                 data.append({'city': city_loop_group, 'state': state_loop_group, 'venues':ven})

          else:
              data.append({'city': city_loop_group, 'state': state_loop_group, 'venues':ven})
              ven=[]
              city_loop_group= area.city
              state_loop_group= area.state
              ven.append({'id':area.id,'name':area.name})
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term= request.form.get('search_term')
  count= Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).count()
  data=Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue=Venue.query.get(venue_id)
  shows=Show.query.all()
  upcoming_shows= []
  past_shows=[]
  for show in shows:
      artist= Artist.query.get(show.artist_id)
      if show.venue_id == venue_id:
          if show.start_time < datetime.now():
              past_shows.append({"artist_id": show.artist_id, "artist_name": artist.name, "artist_image_link": artist.image_link, "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")})
          else:
              upcoming_shows.append({"artist_id": show.artist_id, "artist_name": artist.name, "artist_image_link": artist.image_link, "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")})
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website":venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error=False
    form = VenueForm()
    try:
        # TODO: insert form data as a new Venue record in the db, instead
        # TODO: modify data to be the data object returned from db insertion
        name= request.form['name']
        city=request.form['city']
        state=request.form['state']
        address=request.form['address']
        phone= request.form['phone']
        genres=request.form.getlist('genres')
        facebook_link=request.form['facebook_link']
        image_link= request.form['image_link']
        seeking_talent=bool(request.form['seeking_talent'])
        seeking_description=request.form['seeking_description']

        venue= Venue(name=name,city=city,state=state,address=address,phone=phone,genres=genres,facebook_link=facebook_link,image_link=image_link,seeking_talent=seeking_talent,seeking_description=seeking_description)

        db.session.add(venue)
        db.session.commit()
    except:
        error=True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
        # on successful db insert, flash success
        #flash('Venue ' + request.form['name'] + ' was successfully listed!')
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error=False
    delet_venue= Venue.query.get(venue_id)
    try:
        db.session.delete(delet_venue)
        db.session.commit()
    except:
        error=True
        db.session.rollback()
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term= request.form.get('search_term')
  count= Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).count()
  data=Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  artist=Artist.query.get(artist_id)
  shows=Show.query.all()
  upcoming_shows= []
  past_shows=[]
  for show in shows:
      venue= Venue.query.get(show.venue_id)
      if show.artist_id == artist_id:
          if show.start_time < datetime.now():
              past_shows.append({"venue_id": show.venue_id, "venue_name": venue.name, "venue_image_link": venue.image_link, "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")})
          else:
              upcoming_shows.append({"venue_id": show.venue_id, "venue_name": venue.name, "venue_image_link": venue.image_link, "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")})

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=Artist.query.get(artist_id))

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

    error=False
    form = ArtistForm()
    edited_Artist= Artist.query.get(artist_id)
    try:
        edited_Artist.name= request.form['name']
        edited_Artist.city=request.form['city']
        edited_Artist.state=request.form['state']
        edited_Artist.phone= request.form['phone']
        edited_Artist.genres=request.form.getlist('genres')
        edited_Artist.facebook_link=request.form['facebook_link']
        edited_Artist.image_link= request.form['image_link']
        edited_Artist.seeking_venue=bool(request.form['seeking_venue'])
        edited_Artist.seeking_description=request.form['seeking_description']

        db.session.commit()
    except:
        error=True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Arist ' + request.form['name'] + ' could not be Edited.')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully Edited!')

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=Venue.query.get(venue_id))

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error=False
  form = VenueForm()
  edited_venue= Venue.query.get(venue_id)
  try:
      edited_venue.name= request.form['name']
      edited_venue.city=request.form['city']
      edited_venue.state=request.form['state']
      edited_venue.address=request.form['address']
      edited_venue.phone= request.form['phone']
      edited_venue.genres=request.form.getlist('genres')
      edited_venue.facebook_link=request.form['facebook_link']
      edited_venue.image_link= request.form['image_link']
      edited_venue.seeking_talent=bool(request.form['seeking_talent'])
      edited_venue.seeking_description=request.form['seeking_description']

      db.session.commit()
  except:
      error=True
      db.session.rollback()
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be Edited.')
  else:
      flash('Venue ' + request.form['name'] + ' was successfully Edited!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
      error=False
      form = ArtistForm()
      try:
          name= request.form['name']
          city=request.form['city']
          state=request.form['state']
          phone= request.form['phone']
          genres=request.form.getlist('genres')
          facebook_link=request.form['facebook_link']
          image_link= request.form['image_link']
          seeking_venue=bool(request.form['seeking_venue'])
          seeking_description=request.form['seeking_description']

          artist= Artist(name=name,city=city,state=state,phone=phone,genres=genres,facebook_link=facebook_link,image_link=image_link,seeking_venue=seeking_venue,seeking_description=seeking_description)
          db.session.add(artist)
          db.session.commit()
      except:
          error=True
          db.session.rollback()
      finally:
          db.session.close()
      if error:
          # TODO: on unsuccessful db insert, flash an error instead.
          # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
          flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      else:
          # on successful db insert, flash success
          flash('Artist ' + request.form['name'] + ' was successfully listed!')

      return render_template('pages/home.html')

@app.route('/artists/<artist_id>/delete', methods=['DELETE'])
def artist(artist_id):

    error=False
    delet_artist= Artist.query.get(artist_id)
    try:
        db.session.delete(delet_artist)
        db.session.commit()
    except:
        error=True
        db.session.rollback()
    finally:
        db.session.close()

    return None

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows= Show.query.all()
  data=[]
  for show in shows:
      venue= Venue.query.get(show.venue_id)
      artist= Artist.query.get(show.artist_id)
      data.append({'venue_id': show.venue_id, 'venue_name': venue.name, 'artist_id':show.artist_id, "artist_name": artist.name, "artist_image_link": artist.image_link, "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")})

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error=False
  form = ShowForm()
  try:
      artist_id= request.form['artist_id']
      venue_id=request.form['venue_id']
      start_time=request.form['start_time']

      venue= Venue.query.get(venue_id)
      artist= Artist.query.get(artist_id)

      venue.artists=[artist]
      artist.Venues=[venue]

      show = Show.query.filter(Show.artist_id==artist_id, Show.venue_id==venue_id).all()
      show[0].start_time=start_time

      db.session.commit()
  except:
      error=True
      db.session.rollback()
  finally:
      db.session.close()
  if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Show could not be listed.')
  else:
      # on successful db insert, flash success
      flash('Show was successfully listed!')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
