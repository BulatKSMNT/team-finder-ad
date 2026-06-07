from django.shortcuts import render
from django.core.paginator import Paginator
from .models import IdeaProject
from skills_app.models import ProjectSkill


def show_all_projects(request):
    # Taking all projects from database
    projects_query = IdeaProject.objects.all()

    # Variant 3: filtering by skill tag
    selected_skill = request.GET.get('skill')

    if selected_skill:
        # filter exact match by skill_name
        projects_query = projects_query.filter(required_skills__skill_name=selected_skill)

    # Paginator setup: 12 projects per page
    page_maker = Paginator(projects_query, 12)
    page_number = request.GET.get('page')
    paged_projects = page_maker.get_page(page_number)

    # Get all unique skills to show in the filter panel
    all_tags = ProjectSkill.objects.all().order_by('skill_name')

    context_data = {
        'projects_list': paged_projects,
        'active_skill': selected_skill,
        'all_tags': all_tags
    }

    # Returning html template for main page
    return render(request, 'projects/project_list.html', context_data)
