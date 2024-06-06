# SleepVention: A Data-driven Recommender Platform for Improving Sleep and Wellbeing

## Introduction

SleepVention is designed to help users understand and improve their sleep quality by leveraging data from digital sleep trackers. These trackers provide fine-grained measurements of sleep stages, heart rate, breathing rate, and more, allowing for precise analysis and personalized recommendations. The project focuses on creating a comprehensive web platform where users can upload their sleep data, and researchers can access this data to conduct studies and publish their findings.

## Phase 1: SleepVention Data Repository

Phase 1 focuses on the development of an online data repository. This repository is a web application designed to allow users to connect and upload data from their wearable manufacturer API services (e.g., Fitbit API, Oura API) or aggregator services like Google Health or Apple Health. The repository serves two types of users: normal users and researchers.

### Features for Normal Users:

**Data Upload:** Users can upload their sleep data to the repository.
**Data Visibility and Control:** Users can choose to store their data anonymously or openly and decide if it is visible to others.
**Data Management:** Users can view, manage, and delete their data at any time. They can also see which studies are using their data and how it is being used.
**Graphical Insights:** Users can view graphs and statistics about their sleep patterns and receive personalized recommendations to improve their sleep and wellbeing.

### Features for Researchers:

**Data Access:** Researchers can access users’ data for conducting studies.
**Study Management:** Researchers can publish their studies on the platform.
**Data Monetization:** Users can request monetary compensation for the use of their data in studies.

## Technology Stack
- **Frontend:** HTML, CSS, Bootstrap, JavaScript
- **Backend:** Python, FastAPI
- **Database:** SQLite

