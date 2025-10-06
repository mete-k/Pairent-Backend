# Pairent Backend

Pairent is a supportive mobile platform for parents. It helps users connect with other parents, track child development milestones, access parenting resources, and join forums based on their child’s age or stage.  
This repository contains the **backend** implementation for the Pairent mobile app.

## Features

- **Question Forums:** Parents can post and reply to questions categorized by child age or topic.  
- **Milestone Tracking:** Parents can record and follow their child’s development milestones.  
- **Breakrooms:** Real-time voice chat rooms for parents to relax and connect.  
- **Bibi Chatbot:** AI-powered parenting assistant that answers questions and gives personalized advice.  
- **Nappy & Food Timers:** Serverless backend support for tracking feeding and sleeping schedules.  

## Tech Stack

| Technology | Purpose |
|-------------|----------|
| **AWS Lambda** | Serverless backend functions for scalable logic |
| **Amazon API Gateway** | Routing and exposing APIs to frontend |
| **Amazon Cognito** | Secure authentication and user management |
| **Amazon DynamoDB** | NoSQL database for users, posts, and milestones |
| **Python (Flask)** | Core backend framework for local development |
| **boto3 / AWS SDK** | Communication with AWS services |
| **Amazon Bedrock Agents (Claude)** | AI-powered chatbot (Bibi) integration |
| **Agora SDK** | Real-time voice chat for Breakrooms |

## Team Members

- Elif Bozkurt
- Metehan Kutay
- İdris Onay
- Melda Çiftçi
- Selen Tolan
