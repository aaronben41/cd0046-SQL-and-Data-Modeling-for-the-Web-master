#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
from sre_parse import State
from this import d
from unicodedata import name
from xmlrpc.client import boolean
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, jsonify, flash, redirect, url_for, abort
from flask_moment import Moment
#from flask_sqlalchemy import SQLAlchemy 
#this is commented out, as it has already been imported in models.py
#and its instance db is imported instead
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database
#Connection to local postgresql database had been implemented in config.py

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
#models have been defined in models.py, from where db, Venue, Artist and Show have been imported

      
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
#Slight modifications were made to the date filter as the default definitions produced errors

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
  else:
    date = value
  return babel.dates.format_datetime(date, format, locale='en')

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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  #DONE!
  #A query is done on the Venue table returning all row values across the city and state columns
  data = []
  venue_query = Venue.query.distinct(Venue.city, Venue.state).all()
  for result in venue_query:
    #another query is done to retrieve the locations that exist within the given city and state
    venues = Venue.query.filter_by(city=result.city, state=result.state).all()
    venue_list = []
    for venue in venues:
      venue_list.append({'id': venue.id,'name': venue.name})
    data.append({
    'city': result.city,
    'state': result.state,
    'venues': venue_list
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  #DONE!
  #the ilike attribute is used to take care of case sensitive searches
  search_term = request.form.get('search_term', '')
  search_tag = '%' + search_term + '%'
  search_results = Venue.query.filter(Venue.name.ilike(search_tag)).all()
  #searh_results returns a list, so the number of venues in which the search tag can be found
  #is equivalent to the length of the list
  response={
    "count": len(search_results),
    "data": search_results
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #DONE
  datas = []
  venue_data = Venue.query.all()

  for venue in venue_data:
    show = Show.query.filter(Show.venue_id == venue.id).\
      join(Artist, Artist.id == Show.artist_id).all()
    past_shows = []
    upcoming_shows = []
    
    for x in show:
      if x.start_time >= datetime.now():
        upcoming_shows.append({
          "artist_id": x.artist_id,
          "artist_name": x.artist.name,
          "artist_image_link": x.artist.image_link,
          "start_time": x.start_time    
        })
      else:
        past_shows.append({
          "artist_id": x.artist_id,
          "artist_name": x.artist.name,
          "artist_image_link": x.artist.image_link,
          "start_time": x.start_time 
        })
    venue = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }
    datas.append(venue)
    
  data = list(filter(lambda d: d['id'] == venue_id, datas))[0]

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  #DONE!
  error=False
  try:
    name=request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    genres = request.form.getlist('genres')
    website_link = request.form.get('website_link')
    seeking_talent = request.form.get('seeking_talent', type=boolean)
    seeking_description  = request.form.get('seeking_description')
    
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, 
    genres=genres, image_link=image_link, facebook_link=facebook_link, 
    website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  # TODO: modify data to be the data object returned from db insertion
  finally:
    db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #DONE!
  if error:
    flash('An error occurred. Venue ' + name + ' could not be listed.')  
  # on successful db insert, flash success
  else:
    flash('Venue ' + name + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  #DONE!
  data = Artist.query.all()
  return render_template('pages/artists.html', artists= data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  search_tag = '%' + search_term + '%'
  search_results = Artist.query.filter(Artist.name.ilike(search_tag)).all()
  response = {
    "count": len(search_results),
    "data": search_results
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  #DONE!
  #data = Artist.query.get(artist_id)
  #data = list(filter(lambda d: d['id'] == artist_id, [artist]))[0]
  
  datas = []
  artist_data = Artist.query.all()

  for artist in artist_data:
    show = Show.query.filter(Show.artist_id == artist.id).\
      join(Venue, Venue.id == Show.venue_id).all()
    past_shows = []
    upcoming_shows = []
    for x in show:

      if x.start_time >= datetime.now():
        upcoming_shows.append({
          "venue_id": x.venue_id,
          "venue_name": x.venue.name,
          "venue_image_link": x.venue.image_link,
          "start_time": x.start_time    
        })
      else:
        past_shows.append({
          "venue_id": x.venue_id,
          "venue_name": x.venue.name,
          "venue_image_link": x.venue.image_link,
          "start_time": x.start_time 
        })
    artist = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website_link,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }
    datas.append(artist)
  data = list(filter(lambda d: d['id'] == artist_id, datas))[0]


  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  #DONE!
  error = False
  try:
    
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    website_link = request.form.get('website_link')
    seeking_venue = request.form.get('seeking_venue', type=boolean, default=False)
    seeking_description  = request.form.get('seeking_description')
    artist = Artist.query.get(artist_id)
    artist.name, artist.city, artist.state =name, city, state
    artist.phone, artist.genres, artist.image_link = phone, genres, image_link 
    artist.facebook_link, artist.website_link = facebook_link, website_link 
    artist.seeking_venue, artist.seeking_description = seeking_venue, seeking_description
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + name + ' details could not be updated.')
    return redirect(url_for('show_artist', artist_id=artist_id)) 
  else:
    flash('Artist ' + name + ' records updated successfully.')
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    name = request.form.get('name')
    genres = request.form.getlist('genres')
    address = request.form.get('address')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    website_link = request.form.get('website_link')
    facebook_link = request.form.get('facebook_link')
    seeking_talent = request.form.get('seeking_talent', type=boolean, default=False)
    seeking_description  = request.form.get('seeking_description')
    image_link = request.form.get('image_link')
    venue = Venue.query.get(venue_id)
    venue.name, venue.city, venue.state, venue.address =name, city, state, address
    venue.phone, venue.genres, venue.image_link = phone, genres, image_link 
    venue.facebook_link, venue.website_link = facebook_link, website_link 
    venue.seeking_talent, venue.seeking_description = seeking_talent, seeking_description
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + name + ' details could not be updated.')
  else:
    flash('Venue ' + name + ' records updated successfully.')
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
  # DONE!
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    website_link = request.form.get('website_link')
    seeking_venue = request.form.get('seeking_venue', type=boolean)
    seeking_description  = request.form.get('seeking_description')
    artist = Artist(name=name, city=city, state=state,phone=phone, 
    genres=genres, image_link=image_link, facebook_link=facebook_link, 
    website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
     
  # TODO: modify data to be the data object returned from db insertion
       
  except:
    db.session.rollback()
    error = True
  # on successful db insert, flash success
  finally:
    db.session.close()
  #  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  if error:    
    flash('An error occurred. Artist ' + name + ' could not be listed.')
    return render_template('pages/home.html')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  else:
    flash('Artist ' + name + ' was successfully listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = db.session.query(Show).\
    join(Venue, Venue.id == Show.venue_id).\
      join(Artist, Artist.id == Show.artist_id).all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })

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
  error = False

  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed. Confirm that Artist ID and Venue ID exist')
  else:
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
