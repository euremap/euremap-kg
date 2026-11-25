# EUREMAP SPARQL query results
Run with rdflib against ontology + catalogue graph (2932 triples). Generated 2026-11-19.

## Q01_services_per_step.rq
```sparql
# Q01 — Service count per pipeline step, in pipeline order, with phase
SELECT ?order ?step ?phase (COUNT(?s) AS ?services)
WHERE {
  ?st a eur:PipelineStep ; eur:stepOrder ?order ; skos:prefLabel ?step ; eur:inPhase/skos:prefLabel ?phase .
  OPTIONAL { ?s eur:atPipelineStep ?st }
}
GROUP BY ?order ?step ?phase
ORDER BY ?order
```
Rows: 9

| order | step | phase | services |
|---|---|---|---|
| 1 | Genomics | Genomic & biological resources | 6 |
| 2 | Biomass production | Genomic & biological resources | 2 |
| 3 | Chemical extraction | Chemistry | 8 |
| 4 | Bioassays & bioprofiling | Bioactivity & safety | 15 |
| 5 | Safety and toxicity profiling | Bioactivity & safety | 4 |
| 6 | Chemical profiling | Chemistry | 7 |
| 7 | Chromatography & purification | Chemistry | 9 |
| 8 | Structure elucidation | Chemistry | 13 |
| 9 | Synthesis & semi-synthesis | Chemistry | 7 |

## Q02_country_institution_matrix.rq
```sparql
# Q02 — Country nodes: institutions and services per country
SELECT ?country (COUNT(DISTINCT ?inst) AS ?institutions) (COUNT(?s) AS ?services)
       (GROUP_CONCAT(DISTINCT ?acr; separator=", ") AS ?providers)
WHERE {
  ?s eur:providedBy ?inst .
  ?inst eur:locatedInCountry/skos:prefLabel ?country ; skos:altLabel ?acr .
}
GROUP BY ?country
ORDER BY DESC(?services)
```
Rows: 9

| country | institutions | services | providers |
|---|---|---|---|
| Norway | 2 | 18 | UiT, SINTEF |
| Portugal | 1 | 12 | CCMAR |
| Italy | 2 | 11 | SZN, CNR |
| Germany | 1 | 7 | HZI |
| France | 1 | 6 | SU |
| Spain | 1 | 6 | MEDINA |
| Belgium | 1 | 4 | UGent |
| Israel | 1 | 4 | TAU |
| United Kingdom | 1 | 3 | EMBL-EBI |

## Q03_antimicrobial_embrc.rq
```sparql
# Q03 — Antimicrobial assays (incl. narrower: antibacterial, antifungal, antibiofilm) offered through EMBRC
#        Uses the SKOS hierarchy via skos:broader* so one query finds all sub-types.
SELECT ?id ?title ?provider ?country (GROUP_CONCAT(DISTINCT ?capL; separator="; ") AS ?assays)
WHERE {
  ?cap skos:broader* res:cap-antimicrobial-assay ; skos:prefLabel ?capL .
  ?s eur:hasCapability ?cap ; dct:identifier ?id ; dct:title ?title ;
     eur:offeredThrough res:ri-embrc ;
     eur:providedBy ?p .
  ?p skos:altLabel ?provider ; eur:locatedInCountry/skos:prefLabel ?country .
}
GROUP BY ?id ?title ?provider ?country
ORDER BY ?id
```
Rows: 4

| id | title | provider | country | assays |
|---|---|---|---|---|
| EUREMAP_020 | Evaluation of antimicrobial (antibacterial and antifungal) and antibiofilm activity of extracts or compounds for human health | UGent | Belgium | Antimicrobial assay; Antibiofilm assay; Antibacterial assay; Antifungal assay |
| EUREMAP_021 | Screening for antimicrobial activity (antibacterial) | TAU | Israel | Antimicrobial assay; Antibacterial assay |
| EUREMAP_022 | Screening for antimicrobial, anticancer and antioxidant activities | SZN | Italy | Antimicrobial assay |
| EUREMAP_026 | Screening for antimicrobial, antifungal, lipase, chitinase, collaginase, proteinase, cellulase, amylase, antioxidant activities | CCMAR | Portugal | Antimicrobial assay; Antifungal assay |

## Q04_extraction_scale.rq
```sparql
# Q04 — Chemical-extraction services able to process at least 10 L of culture
SELECT ?id ?provider ?maxLitres ?title
WHERE {
  ?s eur:atPipelineStep res:step-chemical-extraction ; dct:identifier ?id ; dct:title ?title ;
     eur:providedBy/skos:altLabel ?provider ;
     eur:hasCapacity ?q .
  ?q eur:quantityKind res:qk-culture-volume ; schema:unitCode "LTR" ; schema:maxValue ?maxLitres .
  FILTER (?maxLitres >= 10)
}
ORDER BY DESC(?maxLitres)
```
Rows: 2

| id | provider | maxLitres | title |
|---|---|---|---|
| EUREMAP_014 | SINTEF | 40.0 | Extraction of cell pellets from cultures of up to 40 L |
| EUREMAP_010 | MEDINA | 20.0 | Extraction of culture media at scales of up to 20 L |

## Q05_institution_coverage.rq
```sparql
# Q05 — Pipeline coverage per institution (how many of the 9 steps each partner covers)
SELECT ?provider (COUNT(DISTINCT ?st) AS ?stepsCovered) (COUNT(DISTINCT ?s) AS ?services)
       (GROUP_CONCAT(DISTINCT ?n; separator=",") AS ?stepNumbers)
WHERE {
  ?s eur:providedBy/skos:altLabel ?provider ; eur:atPipelineStep ?st .
  ?st skos:notation ?n .
}
GROUP BY ?provider
ORDER BY DESC(?stepsCovered) DESC(?services)
```
Rows: 11

| provider | stepsCovered | services | stepNumbers |
|---|---|---|---|
| SINTEF | 9 | 13 | 01,02,03,04,05,06,07,08,09 |
| CCMAR | 6 | 12 | 03,04,06,07,08,09 |
| SU | 6 | 6 | 02,03,04,06,07,08 |
| HZI | 5 | 7 | 04,06,07,08,09 |
| MEDINA | 5 | 6 | 03,04,06,07,08 |
| UiT | 5 | 5 | 03,04,06,07,08 |
| SZN | 5 | 5 | 03,04,06,07,08 |
| CNR | 4 | 6 | 03,07,08,09 |
| TAU | 4 | 4 | 03,04,07,08 |
| UGent | 2 | 4 | 04,05 |
| EMBL-EBI | 1 | 3 | 01 |

## Q06_domestic_pipeline.rq
```sparql
# Q06 — Which steps can be done entirely within one country? (country × step matrix; gaps = 0)
#        Example: Portugal. Change the ISO code to test another country.
SELECT ?order ?step (COUNT(?s) AS ?servicesInCountry) (GROUP_CONCAT(?id; separator=", ") AS ?ids)
WHERE {
  ?st a eur:PipelineStep ; eur:stepOrder ?order ; skos:prefLabel ?step .
  OPTIONAL {
    ?s eur:atPipelineStep ?st ; dct:identifier ?id ;
       eur:providedBy/eur:locatedInCountry/eur:iso3166Alpha2 "PT" .
  }
}
GROUP BY ?order ?step
ORDER BY ?order
```
Rows: 9

| order | step | servicesInCountry | ids |
|---|---|---|---|
| 1 | Genomics | 0 |  |
| 2 | Biomass production | 0 |  |
| 3 | Chemical extraction | 1 | EUREMAP_013 |
| 4 | Bioassays & bioprofiling | 5 | EUREMAP_023, EUREMAP_024, EUREMAP_025, EUREMAP_026, EUREMAP_030 |
| 5 | Safety and toxicity profiling | 0 |  |
| 6 | Chemical profiling | 1 | EUREMAP_041 |
| 7 | Chromatography & purification | 1 | EUREMAP_049 |
| 8 | Structure elucidation | 2 | EUREMAP_058, EUREMAP_063 |
| 9 | Synthesis & semi-synthesis | 2 | EUREMAP_067, EUREMAP_070 |

## Q07_construct_feedsInto.rq
```sparql
# Q07 — CONSTRUCT step-to-step routing (eur:feedsInto) from I/O contracts
#        A feedsInto B when a typical output of A is a typical input of B.
#        Captures loops such as Chromatography → Bioassays (bioassay-guided fractionation).
CONSTRUCT { ?a eur:feedsInto ?b . }
WHERE {
  ?a eur:typicalOutput ?m .
  ?b eur:typicalInput  ?m .
  FILTER (?a != ?b)
}
```
Result: 12 `eur:feedsInto` triples (saved to `data/derived-feedsInto.ttl`).

## Q07b_routing_table.rq
```sparql
# Q07b — Readable routing table: which step hands which material to which step
SELECT ?from ?material ?to
WHERE {
  ?a eur:typicalOutput ?m ; skos:prefLabel ?from ; eur:stepOrder ?oa .
  ?b eur:typicalInput  ?m ; skos:prefLabel ?to   ; eur:stepOrder ?ob .
  ?m skos:prefLabel ?material .
  FILTER (?a != ?b)
}
ORDER BY ?oa ?ob
```
Rows: 15

| from | material | to |
|---|---|---|
| Biomass production | Microbial biomass / cell pellet | Chemical extraction |
| Biomass production | Culture medium (broth) | Chemical extraction |
| Chemical extraction | Crude extract | Bioassays & bioprofiling |
| Chemical extraction | Crude extract | Chemical profiling |
| Chemical extraction | Crude extract | Chromatography & purification |
| Chromatography & purification | Chromatographic fraction | Bioassays & bioprofiling |
| Chromatography & purification | Purified compound | Bioassays & bioprofiling |
| Chromatography & purification | Chromatographic fraction | Safety and toxicity profiling |
| Chromatography & purification | Purified compound | Safety and toxicity profiling |
| Chromatography & purification | Chromatographic fraction | Chemical profiling |
| Chromatography & purification | Purified compound | Structure elucidation |
| Chromatography & purification | Purified compound | Synthesis & semi-synthesis |
| Structure elucidation | Elucidated chemical structure | Synthesis & semi-synthesis |
| Synthesis & semi-synthesis | Synthetic or semi-synthetic analogue | Bioassays & bioprofiling |
| Synthesis & semi-synthesis | Synthetic or semi-synthetic analogue | Safety and toxicity profiling |

## Q08_accepts_crude_extract.rq
```sparql
# Q08 — Where can I send a crude extract? (service-level statement OR step-level default)
SELECT ?id ?step ?provider ?basis
WHERE {
  {
    ?s eur:acceptsInput res:mat-crude-extract .
    BIND("explicit in service text" AS ?basis)
  } UNION {
    ?s eur:atPipelineStep/eur:typicalInput res:mat-crude-extract .
    FILTER NOT EXISTS { ?s eur:acceptsInput res:mat-crude-extract }
    BIND("step default" AS ?basis)
  }
  ?s dct:identifier ?id ; eur:atPipelineStep/skos:prefLabel ?step ; eur:providedBy/skos:altLabel ?provider .
}
ORDER BY ?id
```
Rows: 31

| id | step | provider | basis |
|---|---|---|---|
| EUREMAP_017 | Bioassays & bioprofiling | UiT | explicit in service text |
| EUREMAP_018 | Bioassays & bioprofiling | MEDINA | step default |
| EUREMAP_019 | Bioassays & bioprofiling | UGent | step default |
| EUREMAP_020 | Bioassays & bioprofiling | UGent | explicit in service text |
| EUREMAP_021 | Bioassays & bioprofiling | TAU | step default |
| EUREMAP_022 | Bioassays & bioprofiling | SZN | explicit in service text |
| EUREMAP_023 | Bioassays & bioprofiling | CCMAR | step default |
| EUREMAP_024 | Bioassays & bioprofiling | CCMAR | step default |
| EUREMAP_025 | Bioassays & bioprofiling | CCMAR | step default |
| EUREMAP_026 | Bioassays & bioprofiling | CCMAR | explicit in service text |
| EUREMAP_027 | Bioassays & bioprofiling | SINTEF | step default |
| EUREMAP_028 | Bioassays & bioprofiling | SU | explicit in service text |
| EUREMAP_029 | Bioassays & bioprofiling | HZI | step default |
| EUREMAP_030 | Bioassays & bioprofiling | CCMAR | step default |
| EUREMAP_031 | Bioassays & bioprofiling | SINTEF | step default |
| EUREMAP_036 | Chemical profiling | UiT | step default |
| EUREMAP_037 | Chemical profiling | MEDINA | step default |
| EUREMAP_038 | Chemical profiling | SZN | step default |
| EUREMAP_039 | Chemical profiling | HZI | step default |
| EUREMAP_040 | Chemical profiling | SINTEF | step default |
| EUREMAP_041 | Chemical profiling | CCMAR | step default |
| EUREMAP_042 | Chemical profiling | SU | step default |
| EUREMAP_043 | Chromatography & purification | UiT | explicit in service text |
| EUREMAP_044 | Chromatography & purification | MEDINA | explicit in service text |
| EUREMAP_045 | Chromatography & purification | TAU | step default |

…6 more rows

## Q09_nmr_via_chmo.rq
```sparql
# Q09 — Cross-ontology query: all services using any technique aligned to CHMO NMR (CHMO:0000591),
#        including narrower EUREMAP concepts (cryoprobe NMR, 1D/2D NMR).
SELECT ?id ?step ?provider (GROUP_CONCAT(DISTINCT ?tech; separator="; ") AS ?techniques)
WHERE {
  ?top skos:exactMatch obo:CHMO_0000591 .
  ?cap skos:broader* ?top ; skos:prefLabel ?tech .
  ?s eur:hasCapability ?cap ; dct:identifier ?id ;
     eur:atPipelineStep/skos:prefLabel ?step ; eur:providedBy/skos:altLabel ?provider .
}
GROUP BY ?id ?step ?provider
ORDER BY ?id
```
Rows: 10

| id | step | provider | techniques |
|---|---|---|---|
| EUREMAP_037 | Chemical profiling | MEDINA | NMR spectroscopy |
| EUREMAP_041 | Chemical profiling | CCMAR | NMR spectroscopy |
| EUREMAP_053 | Structure elucidation | MEDINA | NMR spectroscopy; Cryoprobe NMR |
| EUREMAP_054 | Structure elucidation | TAU | NMR spectroscopy |
| EUREMAP_056 | Structure elucidation | HZI | NMR spectroscopy |
| EUREMAP_057 | Structure elucidation | SINTEF | NMR spectroscopy |
| EUREMAP_058 | Structure elucidation | CCMAR | NMR spectroscopy |
| EUREMAP_059 | Structure elucidation | CNR | NMR spectroscopy |
| EUREMAP_060 | Structure elucidation | SU | NMR spectroscopy |
| EUREMAP_061 | Structure elucidation | MEDINA | NMR spectroscopy; 1D/2D NMR interpretation |

## Q10_no_travel.rq
```sparql
# Q10 — Services usable without travelling (offer remote or virtual access), per step
SELECT ?step (COUNT(DISTINCT ?s) AS ?remoteOrVirtual)
WHERE {
  ?s eur:hasAccessMode ?m ; eur:atPipelineStep ?st .
  ?st skos:prefLabel ?step ; eur:stepOrder ?o .
  FILTER (?m IN (res:access-remote, res:access-virtual))
}
GROUP BY ?step ?o
ORDER BY ?o
```
Rows: 9

| step | remoteOrVirtual |
|---|---|
| Genomics | 6 |
| Biomass production | 1 |
| Chemical extraction | 4 |
| Bioassays & bioprofiling | 15 |
| Safety and toxicity profiling | 4 |
| Chemical profiling | 6 |
| Chromatography & purification | 6 |
| Structure elucidation | 12 |
| Synthesis & semi-synthesis | 7 |

## Q11_national_nodes.rq
```sparql
# Q11 — National nodes (research infrastructure × country) with members and service counts
SELECT ?node (GROUP_CONCAT(DISTINCT ?m; separator=", ") AS ?members) (COUNT(DISTINCT ?s) AS ?services)
WHERE {
  ?n a eur:NationalNode ; skos:prefLabel ?node ; eur:nodeOf ?ri ; eur:locatedInCountry ?c ;
     eur:nodeMember ?inst .
  ?inst skos:altLabel ?m .
  ?s eur:providedBy ?inst ; eur:offeredThrough ?ri .
}
GROUP BY ?node
ORDER BY DESC(?services)
```
Rows: 10

| node | members | services |
|---|---|---|
| EU-OPENSCREEN – Norway | SINTEF, UiT | 18 |
| EMBRC – Portugal | CCMAR | 12 |
| EU-OPENSCREEN – Germany | HZI | 7 |
| EMBRC – France | SU | 6 |
| EU-OPENSCREEN – Spain | MEDINA | 6 |
| EU-OPENSCREEN – Italy | CNR | 6 |
| EMBRC – Italy | SZN | 5 |
| EMBRC – Belgium | UGent | 4 |
| EMBRC – Israel | TAU | 4 |
| EMBL – United Kingdom | EMBL-EBI | 3 |

## Q12_free_and_prereqs.rq
```sparql
# Q12 — Free services and their data-submission prerequisites
SELECT ?id ?title ?repo ?tool
WHERE {
  ?s eur:hasFeeModel res:fee-free ; dct:identifier ?id ; dct:title ?title .
  OPTIONAL { ?s eur:requiresSubmissionTo/skos:prefLabel ?repo }
  OPTIONAL { ?s eur:usesSoftware/<http://www.w3.org/2000/01/rdf-schema#label> ?tool }
}
ORDER BY ?id
```
Rows: 3

| id | title | repo | tool |
|---|---|---|---|
| EUREMAP_001 | Metagenomic read assembly with taxonomic and functional assignments | European Nucleotide Archive (ENA) | MGnify |
| EUREMAP_002 | MAG generation and analysis with quality assessment and taxonomic assignment | European Nucleotide Archive (ENA) | MGnify |
| EUREMAP_003 | Prediction, exploration and analysis of biosynthetic gene clusters from metagenomic datasets | European Nucleotide Archive (ENA) | MGnify |

## Q13_ri_gap_analysis.rq
```sparql
# Q13 — Gap analysis: pipeline steps NOT covered by a given research infrastructure
SELECT ?ri ?order ?missingStep
WHERE {
  ?r a eur:ResearchInfrastructure ; skos:altLabel ?ri .
  ?st a eur:PipelineStep ; eur:stepOrder ?order ; skos:prefLabel ?missingStep .
  FILTER NOT EXISTS { ?s eur:offeredThrough ?r ; eur:atPipelineStep ?st }
}
ORDER BY ?ri ?order
```
Rows: 9

| ri | order | missingStep |
|---|---|---|
| EMBL | 2 | Biomass production |
| EMBL | 3 | Chemical extraction |
| EMBL | 4 | Bioassays & bioprofiling |
| EMBL | 5 | Safety and toxicity profiling |
| EMBL | 6 | Chemical profiling |
| EMBL | 7 | Chromatography & purification |
| EMBL | 8 | Structure elucidation |
| EMBL | 9 | Synthesis & semi-synthesis |
| EMBRC | 1 | Genomics |

## Q14_genome_to_structure_route.rq
```sparql
# Q14 — Assemble a candidate end-to-end route: for each step pick the providers that
#        could take a strain from genome mining to structure (preferring the same country).
SELECT ?order ?step ?country (GROUP_CONCAT(DISTINCT ?acr; separator=", ") AS ?providers)
WHERE {
  VALUES ?st { res:step-genomics res:step-biomass-production res:step-chemical-extraction
               res:step-bioassays res:step-chromatography res:step-structure-elucidation }
  ?st eur:stepOrder ?order ; skos:prefLabel ?step .
  ?s eur:atPipelineStep ?st ; eur:providedBy ?p .
  ?p skos:altLabel ?acr ; eur:locatedInCountry/skos:prefLabel ?country .
  FILTER (STR(?country) IN ("Norway", "France"))
}
GROUP BY ?order ?step ?country
ORDER BY ?order ?country
```
Rows: 11

| order | step | country | providers |
|---|---|---|---|
| 1 | Genomics | Norway | SINTEF |
| 2 | Biomass production | France | SU |
| 2 | Biomass production | Norway | SINTEF |
| 3 | Chemical extraction | France | SU |
| 3 | Chemical extraction | Norway | UiT, SINTEF |
| 4 | Bioassays & bioprofiling | France | SU |
| 4 | Bioassays & bioprofiling | Norway | UiT, SINTEF |
| 7 | Chromatography & purification | France | SU |
| 7 | Chromatography & purification | Norway | UiT, SINTEF |
| 8 | Structure elucidation | France | SU |
| 8 | Structure elucidation | Norway | UiT, SINTEF |

## Q15_keyword_search.rq
```sparql
# Q15 — Free-text service search (what a website search box would call): 'kinase' OR 'antifouling'
SELECT ?id ?title ?provider ?landing
WHERE {
  ?s a eur:Service ; dct:identifier ?id ; dct:title ?title ; dcat:landingPage ?landing ;
     eur:providedBy/skos:altLabel ?provider .
  OPTIONAL { ?s dct:description ?d }
  FILTER (REGEX(CONCAT(STR(?title), " ", COALESCE(STR(?d), "")), "kinase|antifouling", "i"))
}
ORDER BY ?id
```
Rows: 2

| id | title | provider | landing |
|---|---|---|---|
| EUREMAP_019 | Evaluation of antifouling activity for marine and aquatic environments | UGent | https://services.euremap.eu/service/euremap_019/ |
| EUREMAP_028 | Kinase enzymatic assays requiring 250 µg of extract per assay or purified compounds | SU | https://services.euremap.eu/service/euremap_028/ |

## Q16_capability_frequency.rq
```sparql
# Q16 — Most widely offered analytical techniques (aligned to CHMO), with provider count
SELECT ?technique ?chmo (COUNT(DISTINCT ?s) AS ?services) (COUNT(DISTINCT ?p) AS ?providers)
WHERE {
  ?cap skos:broader* res:cap-analytical-technique ; skos:prefLabel ?technique .
  OPTIONAL { ?cap skos:exactMatch|skos:closeMatch ?chmo . FILTER STRSTARTS(STR(?chmo), STR(obo:CHMO_)) }
  ?s eur:hasCapability ?cap ; eur:providedBy ?p .
}
GROUP BY ?technique ?chmo
ORDER BY DESC(?services)
LIMIT 12
```
Rows: 12

| technique | chmo | services | providers |
|---|---|---|---|
| Mass spectrometry | obo:CHMO_0000470 | 17 | 9 |
| High-resolution mass spectrometry | obo:CHMO_0000498 | 15 | 8 |
| Liquid chromatography–mass spectrometry | obo:CHMO_0000524 | 14 | 9 |
| UV/DAD detection | obo:CHMO_0000292 | 12 | 8 |
| HPLC | obo:CHMO_0001009 | 11 | 8 |
| NMR spectroscopy | obo:CHMO_0000591 | 10 | 7 |
| Tandem mass spectrometry (MS/MS, MSn) | obo:CHMO_0000575 | 9 | 8 |
| UHPLC | obo:CHMO_0000795 | 7 | 6 |
| Ion mobility spectrometry | obo:CHMO_0000430 | 6 | 4 |
| Infrared spectroscopy | obo:CHMO_0000630 | 6 | 3 |
| Polarimetry / optical rotation | obo:CHMO_0000779 | 4 | 3 |
| Circular dichroism | obo:CHMO_0000323 | 3 | 2 |
