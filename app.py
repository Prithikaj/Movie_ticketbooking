from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Configuration

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '2005'
app.config['MYSQL_DB'] = 'ticket_booking_db'

mysql = MySQL(app)

# Secret key for flash messages
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/movies')
def movie_list():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM movies')
    movies = cursor.fetchall()
    cursor.close()
    return render_template('movie_list.html', movies=movies)

@app.route('/book/<int:movie_id>', methods=['GET', 'POST'])
def booking(movie_id):
    if request.method == 'POST':
        num_tickets = int(request.form['num_tickets'])
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT seats_available FROM movies WHERE id = %s', (movie_id,))
        seats_available = cursor.fetchone()[0]

        if num_tickets > seats_available:
            flash('Not enough seats available!')
        else:
            cursor.execute('UPDATE movies SET seats_available = seats_available - %s WHERE id = %s', (num_tickets, movie_id))
            cursor.execute('INSERT INTO bookings (movie_id, num_tickets) VALUES (%s, %s)', (movie_id, num_tickets))
            mysql.connection.commit()
            flash('Booking successful!')
            return redirect(url_for('confirmation'))

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM movies WHERE id = %s', (movie_id,))
    movie = cursor.fetchone()
    cursor.close()
    return render_template('booking.html', movie=movie)

@app.route('/confirmation')

def confirmation():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM bookings ORDER BY booking_time DESC LIMIT 1')
    booking = cursor.fetchone()
    cursor.close()
    return render_template('confirmation.html', booking=booking)

if __name__ == '__main__':
    app.run(debug=True)
