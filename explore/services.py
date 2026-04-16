import json
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings


CATEGORY_MAP = {
    "bird": "Aves",
    "insect": "Insecta",
    "mammal": "Mammalia",
    "reptile": "Reptilia",
    "amphibian": "Amphibia",
    "fish": "Actinopterygii",
    "plant": "Plantae",
}

TAXON_ID_MAP = {
    "bird": 3,
    "mammal": 40151,
    "reptile": 26036,
    "amphibian": 20978,
    "insect": 47158,
}

AI_QUERY_HINTS = {
    "bird": ["bird", "birds", "crow", "eagle", "sparrow", "owl", "parrot", "peacock"],
    "insect": ["insect", "insects", "butterfly", "bee", "beetle", "ant", "dragonfly", "moth"],
    "mammal": ["mammal", "mammals", "tiger", "lion", "elephant", "dog", "cat", "monkey"],
    "reptile": ["reptile", "reptiles", "snake", "lizard", "turtle", "crocodile"],
    "amphibian": ["amphibian", "amphibians", "frog", "toad", "salamander"],
    "fish": ["fish", "fishes", "shark", "salmon", "carp", "ray"],
    "plant": ["plant", "plants", "tree", "flower", "grass", "fern", "moss"],
}


def _build_api_url(version, path, params):
    base = settings.INATURALIST_API_BASE.rstrip("/")
    version = version.strip("/")
    path = path.strip("/")
    return f"{base}/{version}/{path}?{urlencode(params)}"


def _build_headers():
    headers = {"Accept": "application/json"}
    if settings.INATURALIST_ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {settings.INATURALIST_ACCESS_TOKEN}"
    return headers


def _extract_results(payload):
    if isinstance(payload, dict):
        if isinstance(payload.get("results"), list):
            return payload["results"], payload.get("total_results")
        if isinstance(payload.get("data"), list):
            meta = payload.get("meta") or {}
            return payload["data"], meta.get("total")
    return [], None


def _normalize_taxon(item):
    default_photo = item.get("default_photo") or item.get("photo") or {}
    conservation = item.get("conservation_status") or item.get("conservation") or {}
    wikipedia_summary = item.get("wikipedia_summary") or item.get("summary") or ""
    preferred_common_name = (
        item.get("preferred_common_name")
        or item.get("common_name")
        or item.get("preferred_common_name_en")
        or "Unknown common name"
    )
    iconic_taxon_name = item.get("iconic_taxon_name") or item.get("iconic_taxon") or item.get("rank") or "Species"

    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "common_name": preferred_common_name,
        "category_label": iconic_taxon_name,
        "image_url": default_photo.get("medium_url") or default_photo.get("square_url") or default_photo.get("url"),
        "summary": wikipedia_summary[:220] if wikipedia_summary else "No summary available from iNaturalist.",
        "observations_count": item.get("observations_count", 0),
        "threatened_status": conservation.get("status_name") or conservation.get("status") or "Not listed",
        "wikipedia_url": item.get("wikipedia_url"),
    }


def _fetch_payload(url):
    request = Request(url, headers=_build_headers())
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def infer_category_from_question(question):
    lowered = question.lower()
    for category, hints in AI_QUERY_HINTS.items():
        if any(hint in lowered for hint in hints):
            return category
    return None


def fetch_inaturalist_species(category=None, query="", per_page=12):
    params = {
        "is_active": "true",
        "rank": "species",
        "per_page": per_page,
    }

    if query.strip():
        params["q"] = query.strip()

    taxon_id = TAXON_ID_MAP.get(category)
    if taxon_id:
        params["taxon_id"] = taxon_id
    else:
        iconic_taxon = CATEGORY_MAP.get(category)
        if iconic_taxon:
            params["iconic_taxa"] = iconic_taxon

    attempted_versions = [settings.INATURALIST_API_VERSION]
    if settings.INATURALIST_API_VERSION != "v1":
        attempted_versions.append("v1")

    last_error = None
    for version in attempted_versions:
        try:
            payload = _fetch_payload(_build_api_url(version, settings.INATURALIST_TAXA_PATH, params))
            raw_results, total_results = _extract_results(payload)
            if raw_results:
                return {
                    "species": [_normalize_taxon(item) for item in raw_results],
                    "total_results": total_results or len(raw_results),
                    "api_version": version,
                }
        except Exception as exc:
            last_error = exc

    if last_error:
        raise last_error

    return {"species": [], "total_results": 0, "api_version": settings.INATURALIST_API_VERSION}


def _normalize_taxon_detail(item):
    default_photo = item.get("default_photo") or {}
    photos = item.get("taxon_photos") or []
    gallery = []

    primary_image = default_photo.get("medium_url") or default_photo.get("square_url") or default_photo.get("original_url") or default_photo.get("url")
    if primary_image:
        gallery.append(primary_image)

    for photo_entry in photos:
        photo = photo_entry.get("photo") or {}
        url = photo.get("medium_url") or photo.get("square_url") or photo.get("original_url") or photo.get("url")
        if url and url not in gallery:
            gallery.append(url)

    if not gallery:
        gallery.append("https://via.placeholder.com/640x480?text=No+Image")

    ancestors = item.get("ancestors") or []
    taxonomy = []
    for rank in ["kingdom", "phylum", "class", "order", "family", "genus"]:
        node = next((ancestor for ancestor in ancestors if ancestor.get("rank") == rank), None)
        if node:
            taxonomy.append(
                (rank, node.get("name") or node.get("preferred_common_name") or "Unknown")
            )

    raw_description = item.get("wikipedia_summary") or item.get("summary") or "No description available from iNaturalist."
    cleaned_description = _clean_text(raw_description)
    abstract = _summarize_text(cleaned_description)
    benefits, risks = _extract_benefits_and_risks(cleaned_description)

    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "common_name": item.get("preferred_common_name") or item.get("common_name") or "Unknown species",
        "scientific_name": item.get("name") or "Unknown scientific name",
        "description": cleaned_description,
        "abstract": abstract,
        "benefits": benefits,
        "risks": risks,
        "gallery": gallery,
        "image_url": gallery[0],
        "taxonomy": taxonomy,
        "iconic_taxon_name": item.get("iconic_taxon_name") or item.get("rank") or "Species",
    }


def _extract_benefits_and_risks(text):
    clean = text.lower()
    benefits = []
    risks = []

    if any(keyword in clean for keyword in ["pollinat", "nectar", "pollen", "flower", "bloom"]):
        benefits.append("Supports pollination and healthy plant reproduction.")
    if any(keyword in clean for keyword in ["seed dispers", "disperses seeds", "seed spread"]):
        benefits.append("Helps disperse seeds and regenerate plant communities.")
    if any(keyword in clean for keyword in ["predat", "prey", "controls pests", "pest control", "eats pests"]):
        benefits.append("Helps control pest populations in the ecosystem.")
    if any(keyword in clean for keyword in ["food source", "food for", "diet of", "feed on", "feeds on"]):
        benefits.append("Serves as a food source for other wildlife.")
    if any(keyword in clean for keyword in ["ecosystem balance", "nutrient cycling", "soil health", "habitat", "ecosystem health"]):
        benefits.append("Contributes to ecosystem balance and habitat health.")

    if "invasive" in clean:
        risks.append("Can become invasive in some regions and outcompete native species.")
    if any(keyword in clean for keyword in ["damage", "damages", "crop", "crops", "agricultur"]):
        risks.append("May damage crops or harm agricultural plants.")
    if any(keyword in clean for keyword in ["disease", "pathogen", "parasite", "infection", "virus", "bacteria"]):
        risks.append("May spread disease or act as a vector for pathogens.")
    if any(keyword in clean for keyword in ["venom", "poison", "toxic", "sting", "bite"]):
        risks.append("Can pose a risk to people or animals through bites or venom.")
    if any(keyword in clean for keyword in ["nuisance", "harmful", "aggressive", "outcompete", "competition"]):
        risks.append("Can become a pest and compete with native species.")

    benefits = list(dict.fromkeys(benefits))[:5]
    risks = list(dict.fromkeys(risks))[:5]

    if not benefits:
        benefits = ["No significant data available"]
    if not risks:
        risks = ["No significant data available"]

    return benefits, risks


def _clean_text(text):
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", str(text))
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def _summarize_text(text, max_chars=220):
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    end = text.find(". ", max_chars)
    if end == -1:
        return text[:max_chars].rstrip() + "..."
    return text[: end + 1].strip()


def fetch_inaturalist_taxon(taxon_id):
    url = _build_api_url(settings.INATURALIST_API_VERSION, f"{settings.INATURALIST_TAXA_PATH}/{taxon_id}", {})
    payload = _fetch_payload(url)
    results, _ = _extract_results(payload)
    if not results:
        return None
    return _normalize_taxon_detail(results[0])


def fetch_inaturalist_observations(taxon_id, per_page=50):
    params = {
        "taxon_id": taxon_id,
        "per_page": per_page,
        "geo": "true",
    }
    url = _build_api_url(settings.INATURALIST_API_VERSION, "observations", params)
    payload = _fetch_payload(url)
    results, _ = _extract_results(payload)

    observations = []
    for item in results:
        latitude = item.get("latitude")
        longitude = item.get("longitude")
        geojson = item.get("geojson") or {}
        if latitude is None or longitude is None:
            coords = geojson.get("coordinates")
            if isinstance(coords, (list, tuple)) and len(coords) == 2:
                longitude, latitude = coords
        if latitude is not None and longitude is not None:
            observations.append({"lat": latitude, "lng": longitude})

    return observations[:per_page]
