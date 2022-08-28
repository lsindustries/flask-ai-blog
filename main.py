from flask import Flask, render_template, request, redirect, url_for, abort, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import config
import aigenerator as blog
import re
import random

app = Flask(__name__)

app.config.from_object(config.config['development'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def page_not_found(e):
    return render_template('404.html'), 404


app.register_error_handler(404, page_not_found)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db = SQLAlchemy(app)


class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)
    featuredimg = db.Column(db.String)


def sanitize_url(url):
    url = url.replace(' ', '_').lower()
    return url


CLEANR = re.compile('<.*?>')

def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext


@app.route('/')
def index():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()

    for post in posts:
        post.date_posted = post.date_posted.strftime('%B %d, %Y')
        post.content = cleanhtml(post.content)
        post.content = post.content[0:250] + "..."
        post.link = sanitize_url(post.title) + '/' + str(post.id)

    return render_template('index.html', posts=posts)


@app.route('/<int:post_id>')
def post(post_id):
    # Load you path with id_product to get nice url (in database)
    post = Blogpost.query.filter_by(id=post_id).one()
    if post_id == post.id:
        path = '/' + sanitize_url(post.title)
    else:
        abort(404)

    return redirect(url_for('friendly_url', links=path, id_product=post_id))


@app.route('/<path:links>/<id_product>')
def friendly_url(links, id_product):
    post = Blogpost.query.filter_by(id=id_product).one()

    date_posted = post.date_posted.strftime('%B %d, %Y')
    product_item = {'id': post.id, 'title': post.title, 'content': post.content, 'author': post.author,
                    'featuredimg': post.featuredimg}

    listed = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    for liste in listed:
        liste.link = sanitize_url(liste.title) + '/' + str(liste.id)

    return render_template('post.html', post=product_item, date_posted=date_posted, listed=listed)


@app.route("/admin")
def admin():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()

    for post in posts:
        post.content = cleanhtml(post.content)
        post.content = post.content[0:150] + "..."
        post.date_posted = post.date_posted.strftime('%B %d, %Y')
        post.link = sanitize_url(post.title) + '/' + str(post.id)

    return render_template("admin.html", posts=posts)


@app.route('/add', methods=["GET", "POST"])
def add():
    if request.method == 'POST':
        title = request.form['title']
        tags = request.form['tags']
        featured = tags.split(',')
        featured = random.choice(featured)
        img = blog.featured_image(featured)
        author = "Admin"
        content = request.form['message']
        if len(title) < 10:
            flash('Title is to short! Min. 10', category='error')
            return render_template("add.html", vcontent=content, vtitle=title, vtags=tags)
        elif len(content) < 10:
            flash('Article is too short!', category='error')
            return render_template("add.html", vcontent=content, vtitle=title, vtags=tags)
        else:

            post = Blogpost(title=title, content=content, date_posted=datetime.now(), featuredimg=img)

            db.session.add(post)
            db.session.commit()
            flash('Post added!', category='success')

        redirect(url_for('index'))

    return render_template("add.html", **locals())


@app.route("/delete-post/<id>")
def delete_post(id):
    post = Blogpost.query.filter_by(id=id).first()
    if not post:
        flash("Post does not exist.", category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted', category='success')
    return redirect(url_for('admin'))


@app.route('/ai-add', methods=["GET", "POST"])
def aigenerator():
    if request.method == 'POST':
        if 'form1' in request.form:
            prompt = request.form['blogTopic']
            blogT = blog.generateBlogTopics(prompt)
            blogTopicIdeas = blogT.replace('\n', '<br>')

        if 'form2' in request.form:
            prompt = request.form['blogSection']
            blogT = blog.generateBlogSections(prompt)
            blogSectionIdeas = blogT.strip().replace('\n', '<br>').replace('- ', '').strip()

            checkSectionIdeas = blogSectionIdeas.split('<br>')
            checkSectionIdeas = list(filter(None, checkSectionIdeas))
            for i in checkSectionIdeas:
                i = i.strip('-')
            infos = enumerate(checkSectionIdeas)

            topic = prompt

        if 'form3' in request.form:
            data = []
            getlist = request.form.getlist('mycheckbox')
            topic = request.form['topic']
            data += getlist
            print(data)
            blogT = blog.blogSectionExpander(data, topic)
            blogExpanded = blogT[1]
            vtitle = blogT[0]

        if 'form4' in request.form:
            title = request.form['title']
            tags = request.form['tags']
            featured = tags.split(',')
            featured = random.choice(featured)
            img = blog.featured_image(featured)
            author = "Admin"
            content = request.form['message']
            if len(title) < 10:
                flash('Title is to short! Min. 10', category='error')
                return render_template("add.html", vcontent=content, vtitle=title, vtags=tags)
            elif len(content) < 10:
                flash('Article is too short!', category='error')
                return render_template("add.html", vcontent=content, vtitle=title, vtags=tags)
            else:

                post = Blogpost(title=title, content=content, author=author, date_posted=datetime.now(),
                                featuredimg=img)

                db.session.add(post)
                db.session.commit()
                flash('Post added!', category='success')

    return render_template('aiadder.html', **locals())


if __name__ == '__main__':
    app.run(debug=True)

