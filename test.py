from src import ReactiveResumeAPI

api = ReactiveResumeAPI(base_url="http://localhost:3000")

print(api.signup(name="John Doe", username="john_doe", email="john.doe@example.com", password="password"))
