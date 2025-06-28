# Creating Tabs

This guide explains how to add a new page that appears as a tab in the MammalBase navigation.

## 1. Create the view

Define a view in `mb/views.py`:

```python
from django.shortcuts import render


def sample_tab(request):
    """Example tab view."""
    return render(request, 'mb/sample_tab.html')
```

## 2. Add a URL pattern

Edit the desired URL configuration, for example `app/urls/root.py`:

```python
from django.urls import path
from mb.views import sample_tab

urlpatterns = [
    # ...
    path('sample-tab/', sample_tab, name='sample_tab'),
]
```

## 3. Create the template

Create `app/mb/templates/mb/sample_tab.html`:

```html
{% raw %}{% extends "mb/base_generic.html" %}

{% block title %}<title>MammalBase - Sample Tab</title>{% endblock %}

{% block content %}
<h2>Sample Tab</h2>
<p>This page demonstrates a new tab.</p>
{% endblock %}{% endraw %}
```

## 4. Link in the navigation

Add the tab to the navigation in `app/mb/templates/mb/base_generic.html`:

```html
<a class="w3-bar-item w3-button w3-hover-white" href="{% raw %}{% url 'sample_tab' %}{% endraw %}">
    Sample Tab
</a>
```

## 5. Optional script

Include client-side logic in the template if needed:

```html
{% raw %}{% block script %}
<script>
  document.addEventListener('DOMContentLoaded', () => {
    console.log('Sample tab loaded');
  });
</script>
{% endblock %}{% endraw %}
```

After adding the above pieces, restart the development server and navigate to `/sample-tab/` to see the new tab.
