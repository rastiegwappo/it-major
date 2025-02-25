from flask import Flask, render_template, url_for, redirect, request, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:tabudlong123@localhost/sample"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

bootstrap = Bootstrap5(app)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(db.Model):
    __tablename__ = "users"  # Renamed table to avoid reserved keyword conflict

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")

    def __repr__(self):
        return self.username

class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)  # Updated ForeignKey
    author = relationship("User", back_populates="posts")

    def __repr__(self):
        return self.title

@app.route("/")
def home():
    users = User.query.all()
    return render_template("home.html", users=users)

@app.route("/users")
def view_users():
    users = User.query.all()
    return render_template("users.html", users=users)

@app.route("/user/<int:id>")
def view_user(id):
    user = User.query.get_or_404(id)
    return render_template("user.html", user=user)

@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
        flash(f"User {username} added successfully")
        return redirect(url_for("home"))
    return render_template("add_user.html")

@app.route("/add_post/<int:user_id>", methods=["GET", "POST"])
def add_post(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        post = Post(title=title, content=content, author=user)
        db.session.add(post)
        db.session.commit()
        flash(f"Post '{title}' added successfully")
        return redirect(url_for("view_user", id=user_id))
    return render_template("add_post.html", user=user)

@app.route("/delete_user/<int:id>")
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully")
    return redirect(url_for("home"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables are created before running
    app.run(debug=True)
