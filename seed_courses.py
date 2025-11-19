from HillSide import create_app
from HillSide.extensions import db
from HillSide.models import Course
from faker import Faker
from datetime import datetime, timedelta
from random import randint, choice

fake = Faker()


def seed_courses(n=30):
    courses = []
    categories = [
        "Python Programming", "Web Development", "Data Science", "Machine Learning",
        "DevOps & Cloud", "Cybersecurity", "Mobile Development", "UI/UX Design",
        "Digital Marketing", "Project Management", "English Language", "Graphic Design"
    ]

    for i in range(30):
        start_date = fake.date_between(start_date='-60d', end_date='+60d')
        duration = randint(4, 12)

        course = Course(
            title=f"{choice(categories)} - {fake.catch_phrase()}",
            description=fake.paragraph(nb_sentences=8),
            image=None,  # or fake.image_url() if you want placeholders
            start_date=start_date,
            duration_weeks=duration,
            total_seats=randint(10, 100) if randint(1, 10) != 1 else None  # 10% unlimited seats
        )
        courses.append(course)
    
    db.session.bulk_save_objects(courses)
    db.session.commit()
    print(f"Inserted {len(courses)} random courses!")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_courses(30)
