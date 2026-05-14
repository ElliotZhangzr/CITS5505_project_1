<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
<div class="container">
    <h1>Register</h1>

    {% if form.errors %}
    <div class="flash-msg error">
        {% for field, errors in form.errors.items() %}
            {% for error in errors %}
                <p>{{ error }}</p>
            {% endfor %}
        {% endfor %}
    </div>
    {% endif %}

    <form method="POST">
        {{ form.hidden_tag() }}
        <input name="username" type="text" placeholder="username" value="{{ form.username.data or '' }}" required>
        <input name="email" type="email" placeholder="email" value="{{ form.email.data or '' }}" required>
        <input name="password" type="password" placeholder="password" required>
        <button type="submit">Register</button>
    </form>
    <p>Already have an account? <a href="/login">Back to login</a></p>
</div>
