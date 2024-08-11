from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    ingredients = db.relationship('Ingredient', backref='recipe', lazy=True)
    portions = db.Column(db.Integer, nullable=False)


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)


if not os.path.exists('instance/recipes.db'):
    with app.app_context():
        db.create_all()
        create_default_user()
        print("Datenbank erstellt.")


@app.route('/')
def index():
    recipes = Recipe.query.all()
    return render_template('index.html', recipes=recipes)


@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe_detail.html', recipe=recipe)


@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        portions = int(request.form['portions'])

        new_recipe = Recipe(title=title, portions=portions)
        db.session.add(new_recipe)
        db.session.commit()

        ingredients = request.form.getlist('ingredient_name')
        amounts = request.form.getlist('ingredient_amount')

        for name, amount in zip(ingredients, amounts):
            ingredient = Ingredient(name=name, amount=int(amount), recipe_id=new_recipe.id)
            db.session.add(ingredient)

        db.session.commit()

        return redirect(url_for('index'))

    return render_template('add_recipe.html')


@app.route('/recipe/<int:recipe_id>/calculate', methods=['POST'])
def calculate_portions(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    new_portions = int(request.form['portions'])
    factor = new_portions / recipe.portions

    scaled_ingredients = {}
    for ingredient in recipe.ingredients:
        scaled_ingredients[ingredient.name] = ingredient.amount * factor

    return render_template('recipe_detail.html', recipe=recipe, scaled_ingredients=scaled_ingredients,
                           new_portions=new_portions)


if __name__ == '__main__':
    app.run(debug=True)
