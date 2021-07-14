# A synthetic data generator for oncogeriatrics

## Summary

Oncogeriatrics is the study of older adults (arbitrarily defined as those 65 years or over) who have cancer. This repository contains the code for a Python implementation of a synthetic data generator for oncogeriatric data. This was developed to simulate and understand how different aspects of physical, mental and social health interact to create risk for adverse outcomes following cancer treatment in older adults.

## Technology

This is an expert-curated, generative, probabilistic synthetic data generator, which starts with conventional probabilistic logic, and then utilises several statistical and supervised machine learning approaches to generate synthetic data: -

1. Distribution generation and random sampling
2. Probabilistic graphical modelling (via the [pgmpy] package)
3. Fuzzy logic (via the [simpful] package)
4. Expert system (the whole system, including internal decision tree logic and curation, could be considered an expert system)

## Evidence basis

Over 300 peer-reviewed publications were utilised to produce this synthetic data generator, alongside expert knowledge. This project formulated the work of a PhD thesis undertaken by the author entitled *"Developing an evidence-based system to facilitate the predictive assessment and optimisation of older adults with cancer"* at [Hull York Medical School], UK. The author is a Clinician Scientist (medical doctor/MD and PhD) and trained as an otolaryngogy surgeon with additional experience in oncogeriatric medicine. His supervisors Professors [Mike Lind] and [Miriam Johnson] are also Clinician Scientists, working as Consultant (Attending) Medical Oncology and Palliative Care physicians respectively. Relevant raw data was extracted from the English Longitudinal Study of Ageing ([ELSA]). Synthetic oncological data was utilised from [Simulacrum], a synthetic data generator for *oncological* data (this synthetic data lacks the *geriatric* components). 

[pgmpy]: https://github.com/pgmpy/pgmpy
[simpful]: https://github.com/aresio/simpful
[Hull York Medical School]: https://www.hyms.ac.uk/
[Mike Lind]: https://www.hyms.ac.uk/about/people/michael-lind
[Miriam Johnson]: https://www.hyms.ac.uk/about/people/miriam-johnson
[ELSA]: https://www.elsa-project.ac.uk/
[Simulacrum]: https://healthdatainsight.org.uk/project/the-simulacrum/

