search_term = request.form.get('search_term', '')
  
  
  
  artist_search = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  response = {
    "count": len(artist_search),
    "data": artist_search
  }