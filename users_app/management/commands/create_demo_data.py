from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from projects_app.models import Project
from skills_app.models import Skill


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей, проекты и навыки для ревью."

    def handle(self, *args, **options):
        User = get_user_model()

        demo_password = "Testpass123!"

        users_data = [
            {
                "email": "anna@example.com",
                "name": "Анна",
                "surname": "Иванова",
                "phone": "+79000000001",
                "github_url": "https://github.com/anna",
                "about": "Backend-разработчик, люблю Django и API.",
            },
            {
                "email": "petr@example.com",
                "name": "Пётр",
                "surname": "Петров",
                "phone": "+79000000002",
                "github_url": "https://github.com/petr",
                "about": "Frontend-разработчик, интересуюсь pet-проектами.",
            },
            {
                "email": "maria@example.com",
                "name": "Мария",
                "surname": "Сидорова",
                "phone": "+79000000003",
                "github_url": "https://github.com/maria",
                "about": "UI/UX-дизайнер и начинающий Python-разработчик.",
            },
        ]

        users = {}

        for user_data in users_data:
            email = user_data["email"]

            user, created = User.objects.get_or_create(
                email=email,
                defaults=user_data,
            )

            if created:
                user.set_password(demo_password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Создан "
                                                     f"пользователь {email}"))
            else:
                updated = False

                for field, value in user_data.items():
                    if getattr(user, field) != value:
                        setattr(user, field, value)
                        updated = True

                if updated:
                    user.save()
                    self.stdout.write(self.style.
                                      WARNING(f"Обновлён пользователь "
                                              f"{email}"))
                else:
                    self.stdout.write(f"Пользователь {email} уже существует")

            users[email] = user

        skill_names = [
            "Python",
            "Django",
            "PostgreSQL",
            "JavaScript",
            "React",
            "Docker",
            "UI/UX",
        ]

        skills = {}

        for skill_name in skill_names:
            skill, _ = Skill.objects.get_or_create(name=skill_name)
            skills[skill_name] = skill

        projects_data = [
            {
                "owner": users["anna@example.com"],
                "name": "API для трекера привычек",
                "description": "Pet-проект для отслеживания полезных "
                               "привычек и статистики.",
                "github_url": "https://github.com/anna/habit-tracker",
                "status": "open",
                "skills": ["Python", "Django", "PostgreSQL", "Docker"],
            },
            {
                "owner": users["petr@example.com"],
                "name": "Витрина pet-проектов",
                "description": "Сайт для публикации и поиска интересных"
                               " проектов.",
                "github_url": "https://github.com/petr/project-showcase",
                "status": "open",
                "skills": ["JavaScript", "React", "Docker"],
            },
            {
                "owner": users["maria@example.com"],
                "name": "Дизайн-система для стартапа",
                "description": "Набор UI-компонентов и правил для "
                               "небольших команд.",
                "github_url": "https://github.com/maria/design-system",
                "status": "open",
                "skills": ["UI/UX", "React"],
            },
        ]

        for project_data in projects_data:
            project_skills = project_data.pop("skills")
            owner = project_data["owner"]
            name = project_data["name"]

            project, created = Project.objects.get_or_create(
                owner=owner,
                name=name,
                defaults=project_data,
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Создан "
                                                     f"проект: {name}"))
            else:
                for field, value in project_data.items():
                    setattr(project, field, value)

                project.save()
                self.stdout.write(self.style.WARNING(f"Обновлён "
                                                     f"проект: {name}"))

            project.participants.add(owner)

            for skill_name in project_skills:
                project.skills.add(skills[skill_name])

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Демо-данные готовы."))
        self.stdout.write("Тестовые пользователи:")
        self.stdout.write("anna@example.com / Testpass123!")
        self.stdout.write("petr@example.com / Testpass123!")
        self.stdout.write("maria@example.com / Testpass123!")
