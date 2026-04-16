from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SignUpForm
from .models import Species
from .services import (
    fetch_inaturalist_species,
    fetch_inaturalist_taxon,
    fetch_inaturalist_observations,
    infer_category_from_question,
)


def entry(request):
    if request.user.is_authenticated:
        return redirect("home")
    return redirect("login")


@login_required
def home(request):
    featured_species = Species.objects.all()[:4]
    category_cards = [
        {"label": "Birds", "key": "bird", "description": "Explore flying species, songbirds, raptors, and water birds."},
        {"label": "Insects", "key": "insect", "description": "Find butterflies, bees, beetles, dragonflies, and more."},
        {"label": "Mammals", "key": "mammal", "description": "Browse wild mammals from forests, grasslands, and cities."},
        {"label": "Reptiles", "key": "reptile", "description": "Discover snakes, lizards, turtles, and crocodilians."},
        {"label": "Amphibians", "key": "amphibian", "description": "See frogs, toads, salamanders, and other wetland species."},
        {"label": "Fish", "key": "fish", "description": "Explore freshwater and marine fish species."},
    ]

    return render(
        request,
        "explore/home.html",
        {
            "featured_species": featured_species,
            "category_cards": category_cards,
            "username": request.user.username,
        },
    )


@login_required
def species_view(request):
    categories = [
        {
            "title": "Birds",
            "description": "Feathered animals that may fly, swim, or perch.",
        },
        {
            "title": "Insects",
            "description": "Small six-legged creatures with diverse shapes and colors.",
        },
        {
            "title": "Mammals",
            "description": "Warm-blooded animals with hair or fur and live young.",
        },
        {
            "title": "Reptiles",
            "description": "Cold-blooded, scaly animals like snakes and lizards.",
        },
        {
            "title": "Amphibians",
            "description": "Moist-skinned animals living in water and on land.",
        },
        {
            "title": "Fish",
            "description": "Gilled animals adapted to freshwater and marine habitats.",
        },
    ]
    return render(request, "explore/species.html", {"categories": categories})


@login_required
def resources_page(request):
    resource_topics = [
        {
            "title": "Nature Conservation",
            "description": "Understand habitat protection, restoration work, wildlife laws, and practical ways to care for ecosystems.",
            "tagline": "Protect wildlife and habitats",
        },
        {
            "title": "Biodiversity",
            "description": "Learn why many species living together helps ecosystems stay healthy, resilient, and productive.",
            "tagline": "The variety of life",
        },
        {
            "title": "Ecology",
            "description": "Explore how organisms interact with climate, food chains, water, soil, and their surrounding environment.",
            "tagline": "How nature connects",
        },
    ]

    return render(request, "explore/resources.html", {"resource_topics": resource_topics})


@login_required
def species_list(request):
    category_param = request.GET.get("category", "").strip()
    query = request.GET.get("q", "").strip()
    api_error = None
    api_species = []
    total_results = 0
    api_version = None
    allowed_categories = {"bird", "insect", "mammal", "reptile", "amphibian", "fish"}

    api_category = category_param if category_param in allowed_categories else None
    try:
        api_response = fetch_inaturalist_species(category=api_category, query=query)
        api_species = api_response["species"]
        total_results = api_response["total_results"]
        api_version = api_response.get("api_version")
    except Exception:
        api_error = "Could not load live species from iNaturalist right now."

    active_category = category_param if category_param in allowed_categories else "all"

    return render(
        request,
        "explore/species_list.html",
        {
            "species_list": api_species,
            "active_category": active_category,
            "search_query": query,
            "api_error": api_error,
            "total_results": total_results,
            "api_version": api_version,
        },
    )


@login_required
def species_detail(request, taxon_id):
    api_error = None
    species = None
    observations = []

    try:
        species = fetch_inaturalist_taxon(taxon_id)
        if not species:
            raise Http404("Species not found")
        observations = fetch_inaturalist_observations(taxon_id, per_page=50)
    except Http404:
        raise
    except Exception:
        api_error = "Could not load species details from iNaturalist right now."

    return render(
        request,
        "explore/species_detail.html",
        {
            "species": species,
            "observations": observations,
            "api_error": api_error,
            "google_api_key": settings.GOOGLE_KG_API_KEY,
        },
    )


@login_required
def ai_helper(request):
    question = request.GET.get("q", "").strip()
    api_error = None
    detected_category = None
    answer_title = None
    results = []
    total_results = 0
    api_version = None

    if question:
        detected_category = infer_category_from_question(question)
        query = question
        if detected_category and question.lower() in {detected_category, f"{detected_category}s"}:
            query = ""

        try:
            api_response = fetch_inaturalist_species(category=detected_category, query=query, per_page=18)
            results = api_response["species"]
            total_results = api_response["total_results"]
            api_version = api_response.get("api_version")
            if detected_category:
                answer_title = f"Detailed {detected_category.title()} results"
            else:
                answer_title = "Detailed species results"
        except Exception:
            api_error = "The AI Helper could not load iNaturalist data right now."

    return render(
        request,
        "explore/ai_helper.html",
        {
            "question": question,
            "detected_category": detected_category,
            "answer_title": answer_title,
            "results": results,
            "total_results": total_results,
            "api_error": api_error,
            "api_version": api_version,
        },
    )


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Your account was created successfully.")
        return response
