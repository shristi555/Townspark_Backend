# sync the project dependencies
uv sync

# apply database migrations
uv run manage.py makemigrations
uv run manage.py migrate

echo "Setup complete."