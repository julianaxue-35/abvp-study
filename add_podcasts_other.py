#!/usr/bin/env python3
"""Inject a single NotebookLM podcast card after the first <p class="lead">
in each target hub. Idempotent: skips a file that already has the card."""
import os

REPO = os.path.expanduser('~/abvp-study')

# relative path -> (audio filename, display title)
TARGETS = {
    'physical-health/euthanasia_hub.html':
        ('euthanasia.m4a', 'Shelter Euthanasia'),
    'physical-health/facility_shelter_design_hub.html':
        ('facility_and_shelter_design.m4a', 'Facility and Shelter Design'),
    'physical-health/sanitation_biosecurity_hub.html':
        ('sanitation_and_biosecurity.m4a', 'Sanitation and Biosecurity'),
    'companion-animal-homelessness/adoption_placement_hub.html':
        ('adoption_floor_work.m4a', 'Adoption Floor Work'),
    'companion-animal-homelessness/access_vet_care_hub.html':
        ('access_vet_care.m4a', 'Access to Veterinary Care'),
    'companion-animal-homelessness/animal_transport_relocation_hub.html':
        ('animal_transport_relocation.m4a', 'Animal Transport and Transfer Programs'),
    'companion-animal-homelessness/shelter_diversion_hub.html':
        ('shelter_diversion.m4a', 'Shelter Diversion Programs'),
    'companion-animal-homelessness/nonsurgical_sterilization_hub.html':
        ('nonsurgical_sterilization.m4a', 'Non-surgical Sterilization'),
    'companion-animal-homelessness/disaster_emergency_hub.html':
        ('disaster_emergency.m4a', 'Disaster and Emergency Response'),
    'shelter-management/01_population_management.html':
        ('population_management.m4a', 'Population Management'),
    'physical-health/parasites_hub.html':
        ('High_Yield_Shelter_Parasitology.m4a', 'High-Yield Shelter Parasitology'),
    'physical-health/medical_health_hub.html':
        ('medical_health.m4a', 'Medical (Non-Infectious) Health'),
    'physical-health/nutrition_husbandry_hub.html':
        ('nutrition_and_husbandry.m4a', 'Nutrition and Husbandry'),
}

MARKER = 'data-podcast-card'


def card(filename, title):
    return (
        f'\n  <div class="card" {MARKER} style="border-left:4px solid #0f3d3a;'
        'background:#eef3f1;border-radius:8px;padding:14px 16px;margin:16px 0">\n'
        '    <h4 style="margin:0 0 6px;display:flex;align-items:center;gap:8px;'
        'color:#0f3d3a">\U0001F3A7 NotebookLM Podcast</h4>\n'
        f'    <p style="color:#5d6b62;margin:0 0 8px;font-size:14px">{title}</p>\n'
        '    <audio controls preload="metadata" style="width:100%">\n'
        f'      <source src="audio/{filename}" type="audio/mp4">\n'
        '    </audio>\n'
        '  </div>'
    )


for rel, (filename, title) in TARGETS.items():
    path = os.path.join(REPO, rel)
    with open(path, encoding='utf-8') as f:
        html = f.read()

    if MARKER in html:
        print(f'  SKIP (already injected)  {rel}')
        continue

    lead = html.find('<p class="lead">')
    if lead == -1:
        print(f'  WARN no <p class="lead"> in  {rel}')
        continue
    end = html.find('</p>', lead) + len('</p>')

    html = html[:end] + card(filename, title) + html[end:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  OK   {rel}')

print('done')
