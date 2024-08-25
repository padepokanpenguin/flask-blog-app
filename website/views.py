from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
import flask_login
from .models import Post, User, Comment, Like
from . import db

views = Blueprint("views", __name__)

@views.route("/")
@flask_login.login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user=flask_login.current_user, posts=posts)

@views.route("/create-post", methods=["GET", "POST"])
@flask_login.login_required
def create_post():
    if (request.method == 'POST'):
        text = request.form.get('text')
        
        if not text:
            flash('Post can\'t be empty', category="error" )
        else:
            post = Post(text=text, author=flask_login.current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.home'))
    return render_template("create_post.html", user=flask_login.current_user)

@views.route("/delete-post/<id>")
@flask_login.login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    
    if not post:
        flash('Post doesnt exist', category="error")
    elif flask_login.current_user.id != post.author:
        flash("You dont have permission to delete this post", category="error")
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')
    
    return redirect(url_for("views.home"))
    
@views.route("/posts/<username>")
@flask_login.login_required
def posts(username):
    user = User.query.filter_by(username=username).first()
    
    if not user:
        flash('No user with that username exists', category="error")
        return redirect(url_for("views.home"))
    
    posts = user.posts
    
    return render_template("posts.html", user=flask_login.current_user, posts=posts)

@views.route("/create-comment/<post_id>", methods=['POST'])
@flask_login.login_required
def create_comment(post_id):
    text = request.form.get("text")
    
    if not text:
        flash("comment cannot be empty", category="error")
    else:
        post = Post.query.filter_by(id=post_id)
        
        if post:
            comment = Comment(text=text, author=flask_login.current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash("Post not found", category="error")
    
    return redirect(url_for("views.home"))

@views.route("/delete-comment/<comment_id>")
@flask_login.login_required
def delete_command(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    
    if not comment:
        flash("comment does\'nt exists", category="error")
    elif comment.author != flask_login.current_user.id and comment.post.author != flask_login.current_user.id:
        flash("You dont have permission to delete this comment", category="error")
    else:
        db.session.delete(comment)
        db.sesssion.save()
        
@views.route("/like-post/<post_id>", methods=['POST'])
@flask_login.login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(author=flask_login.current_user.id, post_id=post_id).first()
    
    if not post:
        return jsonify({"error": "Post not found"}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=flask_login.current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
    
    return jsonify({"likes": len(post.likes), "liked": flask_login.current_user.id in map(lambda x: x.author, post.likes)})
    