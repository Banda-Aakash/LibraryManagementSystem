# app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SECRET_KEY'] = 'abcdef'

db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Define the Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    
    section = db.relationship('Section', backref=db.backref('books', lazy=True))

# Route to render the add book page
@app.route('/add_book/<int:section_id>', methods=['GET'])
def render_add_book(section_id):
    return render_template('addBook.html', section_id=section_id)

# Route to add a book to a section
@app.route('/add_book/<int:section_id>', methods=['POST'])
def add_book_to_section(section_id):
    title = request.form['title']
    author = request.form['author']
    description = request.form['description']
    # Create a new Book object
    new_book = Book(title=title, author=author, description=description, section_id=section_id)
    # Add the new book to the database session
    db.session.add(new_book)
    # Commit the session to save the changes to the database
    db.session.commit()
    # Flash a success message
    flash('Book added successfully!', 'success')
    # Redirect to the librarian dashboard
    return redirect(url_for('librarian_dashboard'))

@app.route('/section_book/<int:section_id>', methods=['GET'])
def render_section_book(section_id):
    section_books = Book.query.filter_by(section_id=section_id).all()
    return render_template('sectionBook.html', books=section_books)

# Route for user login
@app.route('/user_login',methods=['GET'])
def user_loginpg():
    return render_template('userLogin.html')
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            flash('Logged in successfully!', 'success')
            # Set user session
            session['user_id'] = user.id
            # Redirect to user dashboard
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('userLogin.html')


@app.route('/', methods=['GET'])
def home():
    return render_template('userSignUp.html')

@app.route('/user_signup', methods=['GET'])
def user_signuppg():
    return render_template('userSignUp.html')
# Route for user signup

@app.route('/user_signup', methods=['POST'])
def user_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! You can now login.', 'success')
            return redirect(url_for('user_login'))
    return render_template('userSignUp.html')

# Route for user logout
@app.route('/logout', methods=['POST'])
def logout():
    # Clear the user session
    session.pop('user_id', None)
    flash('You have been logged out', 'success')
    # Redirect to the login page
    return redirect(url_for('user_login'))

# Route for adding a book
@app.route('/add_book', methods=['POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        description = request.form['description']

        # Create a new Book object
        new_book = Book(title=title, author=author, description=description)

        # Add the new book to the database session
        db.session.add(new_book)
        
        # Commit the session to save the changes to the database
        db.session.commit()

        # Flash a success message
        flash('Book added successfully!', 'success')

        # Redirect to the user dashboard
        return redirect(url_for('user_dashboard'))

# Route for user dashboard
@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        # If user is not logged in, redirect to login page
        return redirect(url_for('user_login'))

    # Fetch all books from the database
    all_books = Book.query.all()
    
    # Render the user dashboard template and pass the list of books to it
    return render_template('userDashboard.html', all_books=all_books)

# Route to handle search query
@app.route('/search_books', methods=['GET', 'POST'])
def search_books():
    if request.method == 'POST':
        query = request.form['query']
    else:
        query = request.args.get('query', '')

    if query:
        # Perform search in the title and author fields of books
        search_results = Book.query.filter((Book.title.ilike(f'%{query}%')) | (Book.author.ilike(f'%{query}%'))).all()
    else:
        search_results = []
    return render_template('userDashboard.html', search_results=search_results, query=query)


class Librarian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


@app.route('/librarian_signup', methods=['GET'])
def librarian_signuppg():
    return render_template('librarianSignUp.html')

@app.route('/librarian_signup', methods=['POST'])
def librarian_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_librarian = Librarian.query.filter_by(username=username).first()
        if existing_librarian:
            flash('Username already exists. Please choose a different one.', 'danger')
        else:
            new_librarian = Librarian(username=username, password=password)
            db.session.add(new_librarian)
            db.session.commit()
            flash('Account created successfully! You can now login.', 'success')
            return redirect(url_for('librarian_login'))
    return render_template('librarianSignUp.html')

# Route for librarian login
@app.route('/librarian_login', methods=['GET', 'POST'])
def librarian_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        librarian = Librarian.query.filter_by(username=username, password=password).first()
        if librarian:
            flash('Logged in successfully!', 'success')
            # Set librarian session
            session['librarian_id'] = librarian.id
            # Redirect to librarian dashboard
            return redirect(url_for('librarian_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('librarianLogin.html')

# Route for librarian dashboard
@app.route('/librarian_dashboard')
def librarian_dashboard():
    if 'librarian_id' not in session:
        # If librarian is not logged in, redirect to login page
        return redirect(url_for('librarian_login'))
    else :
        sections = Section.query.all()
        return render_template('librarianDashboard.html',sections=sections)
    # Add functionality for librarian dashboard as needed

# Route for librarian logout
@app.route('/librarian_logout', methods=['POST'])
def librarian_logout():
    # Clear the librarian session
    session.pop('librarian_id', None)
    flash('You have been logged out', 'success')
    # Redirect to the login page
    return redirect(url_for('librarian_login'))



class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)

@app.route('/render_section',methods=['GET','POST'])
def render_section():
    return render_template('addSection.html')

@app.route('/add_section', methods=['GET', 'POST'])
def add_section():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        existing_section = Section.query.filter_by(name=name).first()
        if existing_section:
            flash('Section with this name already exists.', 'danger')
        else:
            new_section = Section(name=name, description=description)
            db.session.add(new_section)
            db.session.commit()
            flash('Section added successfully!', 'success')
            return redirect(url_for('librarian_dashboard'))
    return render_template('addSection.html')


# Define the Request model
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    required_days = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref='requests')
    book = db.relationship('Book', backref='requests')


@app.route('/request_book/<int:book_id>', methods=['GET'])
def request_bookpg(book_id):
    return render_template('request.html', book_id=book_id)

@app.route('/request_book/<int:book_id>', methods=['POST'])
def request_book(book_id):
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('You need to login first to request a book.', 'danger')
            return redirect(url_for('user_login'))
        else:
            user_id = session['user_id']
            required_days = request.form['required_days']
            new_request = Request(user_id=user_id, book_id=book_id, required_days=required_days)
            db.session.add(new_request)
            db.session.commit()
            flash('Book requested successfully!', 'success')
            return redirect(url_for('user_dashboard'))
    else:
        flash('Invalid request method.', 'danger')
        return redirect(url_for('user_dashboard'))


# Route for librarian to view requests
@app.route('/view_requests')
def view_requests():
    if 'librarian_id' not in session:
        return redirect(url_for('librarian_login'))
    else:
        requests = Request.query.all()
        return render_template('viewRequests.html', requests=requests)

# Route for librarian to view request details
@app.route('/request_details/<int:request_id>', methods=['GET', 'POST'])
def request_details(request_id):
    if 'librarian_id' not in session:
        return redirect(url_for('librarian_login'))
    else:
        request_item = Request.query.get(request_id)
        if request.method == 'POST':
            action = request.form['action']
            if action == 'grant':
                request_item.status = 'granted'
                borrowed_book = BorrowedBook(user_id=request_item.user_id, book_id=request_item.book_id, borrow_date=datetime.utcnow())
                # Calculate the return date by adding the required days to the borrow date
                required_days = int(request_item.required_days)
                borrowed_book.return_date = borrowed_book.borrow_date + timedelta(days=required_days)
                db.session.add(borrowed_book)
            elif action == 'reject':
                request_item.status = 'rejected'
            db.session.commit()
            flash('Request status updated successfully!', 'success')
            return redirect(url_for('view_requests'))
        return render_template('requestDetails.html', request_item=request_item)

class BorrowedBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='borrowed')

    user = db.relationship('User', backref=db.backref('borrowed_books', lazy=True))
    book = db.relationship('Book', backref=db.backref('borrowed_by', lazy=True))

@app.route('/my_books')
def my_books():
    if 'user_id' not in session:
        # If user is not logged in, redirect to login page
        return redirect(url_for('user_login'))

    # Get the user ID from the session
    user_id = session['user_id']

    # # Fetch all books borrowed by the user from the database
    # borrowed_books = BorrowedBook.query.filter_by(user_id=user_id).all()

    # # Render the My Books template and pass the borrowed books to it
    # return render_template('myBooks.html', borrowed_books=borrowed_books)
     # Retrieve borrowed books
    borrowed_books = BorrowedBook.query.filter_by(user_id=session['user_id'], status='borrowed').all()

    # Retrieve returned books
    returned_books = BorrowedBook.query.filter_by(user_id=session['user_id'], status='returned').all()

    return render_template('myBooks.html', borrowed_books=borrowed_books, returned_books=returned_books)

@app.route('/grant_request/<int:request_id>', methods=['POST'])
def grant_request(request_id):
    if request.method == 'POST':
        # Get the request item from the database based on the request_id
        request_item = Request.query.get_or_404(request_id)

        # Check if the request is pending
        if request_item.status == 'pending':
            # Update the status of the request to 'granted'
            request_item.status = 'granted'

            # Create a new entry in the BorrowedBook table
            new_borrowed_book = BorrowedBook(user_id=request_item.user_id, book_id=request_item.book_id)
            db.session.add(new_borrowed_book)
            db.session.commit()

            # Redirect the user to the request details page
            return redirect(url_for('request_details', request_id=request_id))
        else:
            # If the request is not pending, handle the error
            flash('Request is not pending.', 'danger')
            return redirect(url_for('view_requests'))
    else:
        # If the request method is not POST, handle the error
        flash('Invalid request method.', 'danger')
        return redirect(url_for('view_requests'))

@app.route('/return_book/<int:borrowed_book_id>', methods=['POST'])
def return_book(borrowed_book_id):
    borrowed_book = BorrowedBook.query.get(borrowed_book_id)
    if borrowed_book:
        borrowed_book.return_date = datetime.utcnow()
        borrowed_book.status = 'returned'
        db.session.commit()
        flash('Book returned successfully!', 'success')
    else:
        flash('Borrowed book not found!', 'danger')
    return redirect(url_for('user_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
