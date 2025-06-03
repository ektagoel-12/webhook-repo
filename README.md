# GitHub Webhook Monitoring System

A real-time monitoring system that captures GitHub repository events through webhooks and displays them in a clean, responsive web interface with automatic polling updates.

## Overview

This project demonstrates a complete webhook integration workflow where GitHub repository events (push, pull request, merge) are automatically captured, stored in MongoDB, and displayed in a live dashboard that updates every 15 seconds.

## Key Features

- Real-time Event Capture: Automatically receives GitHub webhook events
- Live Dashboard: Updates every 15 seconds with latest repository activities
- Event Formatting: Professional display with timestamps and author information
- RESTful API: Clean endpoints for webhook processing and data retrieval
- Responsive Design: Mobile-friendly interface with minimal styling
- Persistent Storage: MongoDB integration for event history

## Supported Events

### Push Events
Format: {author} pushed to {to_branch} on {timestamp}
Example: "John Doe pushed to main on 1st June 2025 - 2:30 PM UTC"

### Pull Request Events
Format: {author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}
Example: "Jane Smith submitted a pull request from feature to main on 1st June 2025 - 1:15 PM UTC"

### Merge Events
Format: {author} merged branch {from_branch} to {to_branch} on {timestamp}
Example: "Mike Johnson merged branch develop to main on 1st June 2025 - 3:45 PM UTC"
