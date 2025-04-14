# ☁️ Cloud Development Project: GPT Data Tagger and Analyzer

Welcome to the **Cloud Development project of GPT Data Tagger and Analyzer**.

This project focuses on **cyber threat data tagging and analyzing**, enabling the system to use this specific domain knowledge base to answer cyber security-related user prompts in real time. By establishing a clear framework, the document aims to guide the project team and stakeholders through the **design architecture**, ensuring an efficient **deployment process** and smooth **system usage**.

---

##  Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [About this Repository](#about-this-repository)
4. [Pre-requisites](#pre-requisites)
5. [Getting Started](#getting-started)
6. [Customizing the Deployment](#customizing-the-deployment)
7. [Chat Interface](#chat-interface)
8. [Predefined Prompts Execution](#predefined-prompts-execution)
9. [Attack Vectors Details](#attack-vectors-details)
10. [Pinecone Integration](#pinecone-integration)
11. [Resources Used](#resources-used)
12. [Contact](#contact)
13. [License](#license)

---

##  Project Overview

Cyber threats are rapidly evolving, and organizations need a **proactive approach** to detect them.

There should be a way to retrieve **cyber threat-related data in real-time**. However, most current LLMs (Large Language Models) suffer from limitations such as:

- Cut-off date constraints
- Randomness in responses
- Outdated or generic answers
- Non-authoritative sources
- Confusing cybersecurity terminology

To address these issues, we aim to **extend LLM capabilities** by integrating them with **specific domains** or an **organization’s internal knowledge base**, without the need to retrain the models.

---

##  System Architecture

![System Architecture](https://github.com/user-attachments/assets/09dac7cd-8ea2-4cd6-a988-8113ac67e9f0)

---

##  About this Repository

The application is deployed on **cloud infrastructure** using **AWS services**, ensuring **reliability** and **scalability**.

### Key Components:
- **AWS Lambda Functions**: For processing incoming data and performing threat analysis serverlessly.
- **Amazon DynamoDB**: For securely storing structured threat records.
- **Amazon S3**: For managing unstructured data (e.g., reports, logs).
- **Amazon API Gateway**: To expose the analysis functions as **RESTful endpoints** for secure and authenticated access.
- **Amazon CloudWatch**: Used to schedule and monitor **Lambda executions**, ensuring timely updates of the **GPT-based analysis module**.


