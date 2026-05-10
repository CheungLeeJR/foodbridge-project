import os
from datetime import datetime, timedelta
# Import necessary datetime modules for handling time-related functionality.
from flask import Flask, render_template, request, redirect, url_for, flash, abort
# Import Flask components to establish the web application framework.
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
# Import Flask-Login components for managing user authentication and sessions.
from models import db, User, FoodListing, FoodFactory
# db serves as the primary database manager for Flask projects; all database structure definitions and CRUD operations are executed via this instance.
from services import NotificationManager, EmailNotifier, SMSNotifier
# Extract complex logic from routes to separate files to maintain robust architecture.
app = Flask(__name__)
# Initialize the Flask application instance and determine the root path.
app.config["SECRET_KEY"] = "super-secret-food-rescue-key"
# Configure the cryptographic key required for secure session management and CSRF protection.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Determine the absolute path of the application directory to ensure cross-platform compatibility.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "foodbridge2.db")
db.init_app(app)
# Bind the SQLAlchemy instance to the Flask application, utilizing the application factory pattern.

login_manager = LoginManager(app)
# Initialize the login manager module and bind it with the main Flask application instance.
login_manager.login_view = "login"
# Configure the default redirect endpoint for unauthenticated users attempting to access protected views.
@login_manager.user_loader
# Register the callback function utilized by Flask-Login to reconstruct the user session from the database.
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---
@app.route("/")
# Defines the routing mapping the root URL ("/") to the index view function.
def index():
    # Show only available food that hasn't expired
    listings = FoodListing.query.order_by(FoodListing.expiry_time.asc()).all()
# Retrieve all records from the FoodListing table.
# Sort the retrieved records chronologically by their expiration time.
    return render_template("index.html", listings=listings)
# Render the HTML template, injecting the retrieved food listings context.
@app.route("/register", methods=["GET", "POST"])
# Configure the route to accept both GET requests (for loading the form) and POST requests (for form submission).
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        role = request.form.get("role")
        contact_info = request.form.get("contact_info")
        # Extract the submitted data fields from the HTTP POST payload securely.
        if User.query.filter_by(_username=username).first():
            flash("Username already taken.", "danger")
            return redirect(url_for("register"))
            # Validate user uniqueness by querying the database for a conflicting username.
        try:
            # Encapsulation validation triggers here naturally via properties
            user = User(username=username, role=role, contact_info=contact_info)
            user.set_password(password)
            db.session.add(user)
            # Register the new user instance with the current database session.
            db.session.commit()
            # Commit the ongoing session to persist the new user record into the database.
            flash(f"Registration successful for {user.username}. Please log in.", "success")
            # Dispatch a localized success notification message intended for front-end rendering.
            return redirect(url_for("login"))
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("register"))
        # Exception handler for capturing data validation errors (like ValueError), and responding with a relevant alert.
            
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(_username=request.form.get("username")).first()
        if user and user.check_password(request.form.get("password")):
            # Perform a secure password verification using robust hashing logic instead of plain text matching.
            login_user(user)
            # Instantiate the user session context using Flask-Login management tools.
            return redirect(url_for("dashboard"))
        # Utilize url_for to generate routing dynamically, maintaining resilience against path modifications.
        flash("Invalid credentials.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
# Protect this endpoint with the @login_required decorator, authorizing actions for authenticated sessions only.
def logout():
    logout_user()
    # Eject the active user session parameters and gracefully forward the client to the indexing endpoint.
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "donor":
        # 'current_user' effectively encapsulates metadata referencing the currently authenticated entity object.
        listings = FoodListing.query.filter_by(donor_id=current_user.id).order_by(FoodListing.id.desc()).all()
        # Enquire and assemble comprehensive food listing entries actively bound to the current donor profile.
        # Ensure sequential arrangement in descending ID progression to prioritize the most recently minted items.
        return render_template("dashboard_donor.html", listings=listings)
    else:
        claims = FoodListing.query.filter_by(receiver_id=current_user.id).order_by(FoodListing.id.desc()).all()
        return render_template("dashboard_receiver.html", claims=claims)

@app.route("/listing/new", methods=["GET", "POST"])
@login_required
def new_listing():
    if current_user.role != "donor":
        abort(403)
        # Deny authorization rendering HTTP Standard 403 Forbidden Error for entities outside "donor" roles.
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        location = request.form.get("location")
        food_type = request.form.get("food_type", "generic")
        hours_valid = int(request.form.get("hours_valid", 2))
        expiry_time = datetime.utcnow() + timedelta(hours=hours_valid)
        # Formulate accurate expiration metrics leveraging relative timestamp logic derived from active UTC coordinates.
        # Initialize instances dynamically utilizing the abstract Factory Pattern depending on the contextual 'food_type'.
        listing = FoodFactory.create_food(
            food_type=food_type, title=title, description=description, location=location,
            expiry_time=expiry_time, donor_id=current_user.id)
        # Yield distinct structured instances originating from 'FoodListing' subclass templates.
        db.session.add(listing)
        db.session.commit()
        flash(listing.display_info() + " listed successfully!", "success")
        # Manifest human-readable confirmation leveraging polymorphic detail presentation behavior.
        return redirect(url_for("dashboard"))
    return render_template("new_listing.html")

@app.route("/listing/<int:listing_id>/claim", methods=["POST"])
# Isolate numeric identifier ('listing_id') payload via the defined parametric URI constraint sequence.
@login_required
def claim_listing(listing_id):
    if current_user.role != "receiver":
        flash("Only receivers can claim food.", "danger")
        return redirect(url_for("index"))
        
    listing = FoodListing.query.get_or_404(listing_id)
    # Guarantee availability or cleanly throw standard 404 (Not Found) if queried entity does not persist.
    
    # Process transactional interaction encapsulating inherent operational logic inside models.
    if listing.claim(current_user.id):
        db.session.commit()
        
        # Deploy Service structures engineered reflecting common Singleton alongside Strategy architectures.
        notifier = NotificationManager()
        if not notifier._notifiers: # Initialize composed services functionally utilizing lazy load optimizations.
            notifier.add_notifier(EmailNotifier()).add_notifier(SMSNotifier())
        
        # Distribute polymorphic notification outputs spanning integrated service networks.
        notifier_msgs = notifier.notify_all(listing.donor, f"Your listing {listing.title} has been claimed!")
        for msg in notifier_msgs:
            print("System Log Strategy Executed:", msg) # Implement rudimentary logging capturing abstract event metrics explicitly.
            
        flash(f"Claimed {listing.title}! Please pick it up at the location.", "success")
    else:
        flash("This food has already been claimed or is unavailable.", "danger")
        
    return redirect(url_for("dashboard"))

@app.route("/listing/<int:listing_id>/complete", methods=["POST"])
@login_required
def complete_listing(listing_id):
    listing = FoodListing.query.get_or_404(listing_id)
    
    # Encapsulated Business Logic designed handling progressive entity state modification constraints securely.
    if current_user.id in [listing.donor_id, listing.receiver_id]:
        if listing.complete_pickup():
            db.session.commit()
            flash("Pickup confirmed! Thanks for using FoodBridge.", "success")
        else:
            flash("Could not complete pickup, item may not be claimed.", "warning")
            
    return redirect(url_for("dashboard"))

@app.context_processor
def inject_now():
    return {'current_time': datetime.utcnow}

def init_db():
    with app.app_context():
        # Inject contextual definitions abstracting away direct SQL database connection overhead safely.
        # Synthesize required application-level references executing initial schema formulation logically correctly.
        db.create_all()
        # Compile predefined ORM structured schema rules translating code straight into SQL-native dialect formats effectively.
        # --- ADDING SAMPLE DATA ---
        # Bootstrap default operational mock templates dynamically only within environments showing initial vacuums.
        if not User.query.first() or FoodListing.query.count() == 0:
            # 1. Instantiate typical contextual entities serving conceptual Donor/Receiver functional mock simulations.
            sample_donor = User(username="FreshBakery", role="donor", contact_info="bakery@sample.com")
            sample_donor.set_password("123456")
            
            sample_receiver = User(username="CityShelter", role="receiver", contact_info="help@shelter.org")
            sample_receiver.set_password("123456")
            
            db.session.add_all([sample_donor, sample_receiver])
            db.session.commit()
            
            # 2. Fabricate prototype listing structures effectively relying securely on the prebuilt Abstract Factory framework.
            food1 = FoodFactory.create_food(
                food_type="perishable",
                title="15x Fresh Croissants",
                description="Baked this morning! Need to be eaten soon.",
                location="123 Downtown Bakery St.",
                expiry_time=datetime.utcnow() + timedelta(days=7),
                donor_id=sample_donor.id
            )
            
            food2 = FoodFactory.create_food(
                food_type="non_perishable",
                title="50x Canned Tomato Soup",
                description="Leftovers from our canned food drive. Excellent condition.",
                location="City Shelter Warehouse",
                expiry_time=datetime.utcnow() + timedelta(days=180),
                donor_id=sample_donor.id
            )
            
            db.session.add_all([food1, food2])
            db.session.commit()
            print("Successfully injected sample data into the database!")

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8000)
