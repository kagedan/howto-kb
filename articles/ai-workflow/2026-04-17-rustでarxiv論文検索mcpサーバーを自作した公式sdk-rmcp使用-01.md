---
id: "2026-04-17-rustでarxiv論文検索mcpサーバーを自作した公式sdk-rmcp使用-01"
title: "RustでarXiv論文検索MCPサーバーを自作した（公式SDK rmcp使用）"
url: "https://zenn.dev/aisumairu/articles/1f0933af3b1969"
source: "zenn"
category: "ai-workflow"
tags: ["MCP", "API", "zenn"]
date_published: "2026-04-17"
date_collected: "2026-04-18"
summary_by: "auto-rss"
query: ""
---

```
[
  {
    "arxiv_id": "1808.09954",
    "title": "The Star-Planet Activity Research CubeSat (SPARCS): A Mission to Understand the Impact of Stars in Exoplanets",
    "authors": [
      "David R. Ardila",
      "Evgenya Shkolnik",
      "Paul Scowen",
      "April Jewell",
      "Shouleh Nikzad",
      "Judd Bowman",
      "Michael Fitzgerald",
      "Daniel Jacobs",
      "Constance Spittler",
      "Travis Barman",
      "Sarah Peackock",
      "Matthew Beasley",
      "Varoujan Gorgian",
      "Joe Llama",
      "Victoria Meadows",
      "Mark Swain",
      "Robert Zellem"
    ],
    "abstract": "The Star-Planet Activity Research CubeSat (SPARCS) is a NASA-funded astrophysics mission, devoted to the study of the ultraviolet (UV) time-domain behavior in low-mass stars. Given their abundance and size, low-mass stars are important targets in the search for habitable-zone, exoplanets. However, not enough is known about the stars flare and quiescent emission, which powers photochemical reactions on the atmospheres of possible planets. Over its initial 1-year mission, SPARCS will stare at ~10 stars in order to measure short- (minutes) and long- (months) term variability simultaneously in the near-UV (NUV - lam = 280 nm) and far-UV (FUV - lam = 162 nm). The SPARCS payload consists of a 9-cm reflector telescope paired with two high-sensitivity 2D-doped CCDs. The detectors are kept passively cooled at 238K, in order to reduce dark-current contribution. The filters have been selected to provide strong rejection of longer wavelengths, where most of the starlight is emitted. The payload will be integrated within a 6U CubeSat to be placed on a Sun-synchronous terminator orbit, allowing for long observing stares for all targets. Launch is expected to occur not earlier than October 2021.",
    "url": "https://arxiv.org/abs/1808.09954v1",
    "pdf_url": "https://arxiv.org/pdf/1808.09954v1",
    "published_date": "2018-08-29",
    "categories": [
      "astro-ph.IM",
      "astro-ph.EP",
      "astro-ph.SR"
    ]
  },
  {
    "arxiv_id": "1907.07634",
    "title": "CubeSats for Astronomy and Astrophysics",
    "authors": [
      "Ewan S. Douglas",
      "Kerri L. Cahoy",
      "Mary Knapp",
      "Rachel E. Morgan"
    ],
    "abstract": "CubeSats have the potential to expand astrophysical discovery space, complementing ground-based electromagnetic and gravitational-wave observatories. The CubeSat design specifications help streamline delivery of instrument payloads to space. CubeSat planners have more options for tailoring orbits to fit observational needs and may have more flexibility in rapidly rescheduling observations to respond to transients. With over 1000 CubeSats launched, there has been a corresponding increase in the availability and performance of commercial-off-the-shelf (COTS) components compatible with the CubeSat standards, from solar panels and power systems to reaction wheels for three axis stabilization and precision attitude control. Commercially available components can reduce cost CubeSat missions, allowing more resources to be directed toward scientific instrument payload development and technology demonstrations.",
    "url": "https://arxiv.org/abs/1907.07634v2",
    "pdf_url": "https://arxiv.org/pdf/1907.07634v2",
    "published_date": "2019-07-17",
    "categories": [
      "astro-ph.IM"
    ]
  },
  {
    "arxiv_id": "2408.06454",
    "title": "TESERACT: Twin Earth SEnsoR Astrophotonic CubesaT",
    "authors": [
      "Tyler deLoughery",
      "Clayton Lauzon",
      "Haydn Sims",
      "Wahab Almuhtadi",
      "Ross Cheriton"
    ],
    "abstract": "In this paper, we evaluate the viability of CubeSats as an attractive platform for lightweight instrumentation by describing a proof of concept CubeSat that houses an astrophotonic chip for transit spectroscopy-based exoplanet atmosphere gas sensing. The Twin Earth SEnsoR Astrophotonic CubesaT (TESERACT) was designed to house a correlation spectroscopy chip along with an electrical and optical system for operation. We investigate design challenges and considerations in incorporating astrophotonic instrumentation such as component integration, thermal management and optical alignment. This work aims to be a pathfinder for demonstrating that astrophotonic-based CubeSat missions can perform leading edge, targeted science in lower-cost CubeSat platforms.",
    "url": "https://arxiv.org/abs/2408.06454v1",
    "pdf_url": "https://arxiv.org/pdf/2408.06454v1",
    "published_date": "2024-08-12",
    "categories": [
      "astro-ph.IM",
      "cond-mat.mes-hall",
      "physics.app-ph",
      "physics.ins-det"
    ]
  },
  {
    "arxiv_id": "1701.08201",
    "title": "Optical Navigation for Interplanetary CubeSats",
    "authors": [
      "Stephen R. Schwartz",
      "Shota Ichikawa",
      "Pranay Gankidi",
      "Nalik Kenia",
      "Graham Dektorand Jekan Thangavelautham"
    ],
    "abstract": "CubeSats and small satellites are emerging as low-cost tools for performing science and exploration in deep space. These new classes of satellite exploit the latest advancement in miniaturization of electronics, power systems, and communication technologies to promise reduced launch cost and development cadence. JPL's MarCO CubeSats, part of the Mars Insight mission, will head on an Earth escape trajectory to Mars in 2018 and serve as communication relays for the Mars Insight Lander during Entry, Descent and Landing. Incremental advancements to the MarCO CubeSats, particularly in propulsion and GNC, could enable these spacecraft to get to another planet or to Near Earth Objects. This can have substantial science return with the right science instrument. We have developed an interplanetary CubeSat concept that includes onboard green monopropellant propulsion system and that can get into a capture orbit around a neighboring planet or chase a small-body. One such candidate is the Martian moon Phobos. Because of the limits of current CubeSat hardware and lack of an accurate ephemeris of Phobos, there will be a 2 to 5 km uncertainty in distance between the spacecraft and Phobos. This presents a major GNC challenge when the CubeSat first attempts to get into visual range of the moon. One solution to this challenge is to develop optical navigation technology that enables the CubeSat to take epicyclic orbits around the most probable location of the target, autonomously search and home-in on the target body. In worst-case scenarios, the technology would narrow down the uncertainty of the small-body location and then use optical flow, a computer vision algorithm to track movement of objects in the field of view. A dimly lit small-body can be detected by the occlusion of one or more surrounding stars. Our studies present preliminary simulations that support the concept.",
    "url": "https://arxiv.org/abs/1701.08201v1",
    "pdf_url": "https://arxiv.org/pdf/1701.08201v1",
    "published_date": "2017-01-26",
    "categories": [
      "astro-ph.IM"
    ]
  },
  {
    "arxiv_id": "2512.03329",
    "title": "Push-broom Mapping of Galaxies and Supernova Remnants with the SPRITE CubeSat",
    "authors": [
      "Elena Carlson",
      "Brian Fleming",
      "Yi Hang Valerie Wong",
      "Briana Indahl",
      "Dmitry Vorobiev",
      "Maitland Bowen",
      "Donal O'Sullivan",
      "Kevin France",
      "Anne Jaskot",
      "Jason Tumlinson",
      "Sanchayeeta Borthakur",
      "Michael Rutkowski",
      "Stephan McCandliss",
      "Ravi Sankrit",
      "John M. O'Meara"
    ],
    "abstract": "Supernovae (SNe) enrich and energize the surrounding interstellar medium (ISM) and are a key mechanism in the galaxy feedback cycle. The heating of the ISM by supernova shocks, and its subsequent cooling is critical to future star formation. The cooling of the diffuse shock-heated ISM is dominated by ultraviolet (UV) emission lines. These cooling regions and interfaces have complex spatial structure on sub-parsec scales. Mapping this cooling process is essential to understanding the feedback cycle of galaxies, a major goal of the 2020 Astrophysics Decadal Survey. The Supernova remnants and Proxies for ReIonization Testbed Experiment (SPRITE) CubeSat Mission will house the first long-slit orbital spectrograph with sub-arcminute angular resolution covering far ultraviolet wavelengths (FUV; 1000 - 1750 angstroms) and access to the Lyman UV (lambda < 1216 angstroms). SPRITE aims to provide new insights into the stellar feedback that drives galaxy evolution by mapping key FUV emission lines at the interaction lines between supernova remnants (SNRs) and the ambient interstellar medium (ISM). SPRITE will also measure the ionizing escape from approximately 50 low-redshift (0.16 < z < 0.4) star-forming galaxies. Current models predict SPRITE capable of detecting strong O VI, O IV], and C IV emission lines with angular resolution from 10 - 20 arcseconds. The SPRITE SNR survey will use push-broom mapping of its long-slit on extended sources to produce the first large sample of sub-arcminute 3D data cubes of extended sources in the FUV. In this paper, we present simulated SPRITE observations of Large Magellanic Cloud (LMC) SNRs to demonstrate the efficacy of the SPRITE instrument ahead of launch and instrument commissioning. These models serve as critical planning tools and incorporate the final pre-flight predicted performance of the instrument and the early extended source data reduction pipeline.",
    "url": "https://arxiv.org/abs/2512.03329v1",
    "pdf_url": "https://arxiv.org/pdf/2512.03329v1",
    "published_date": "2025-12-03",
    "categories": [
      "astro-ph.IM",
      "astro-ph.GA"
    ]
  }
]
```
